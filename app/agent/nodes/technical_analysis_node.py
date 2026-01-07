"""Nodo: obtiene SMAs y genera análisis técnico con LLM."""

from __future__ import annotations

import logging
from datetime import datetime
from typing import List

from app.agent.state.agent_state import AgentState
from app.clients.indicators_sma_client import IndicatorClientError, sma_client
from app.models.technical_analysis_models import TechnicalAnalysis
from app.utils.agent_executor import AgentExecutorError, agent_executor

logger = logging.getLogger(__name__)


def _format_sma_values_for_prompt(
    *, sma_25_values: List[tuple[datetime, float]], sma_200_values: List[tuple[datetime, float]]
) -> str:
    """Formatea valores de SMAs para el prompt del LLM.

    Args:
        sma_25_values: Lista de tuplas (fecha, valor) para SMA 25.
        sma_200_values: Lista de tuplas (fecha, valor) para SMA 200.

    Returns:
        str: Texto formateado con las SMAs.
    """

    lines = ["SMA 25 (últimos 10 valores):"]
    for date, value in sma_25_values[:10]:
        lines.append(f"  {date.strftime('%Y-%m-%d')}: ${value:,.2f}")

    lines.append("\nSMA 200 (últimos 10 valores):")
    for date, value in sma_200_values[:10]:
        lines.append(f"  {date.strftime('%Y-%m-%d')}: ${value:,.2f}")

    return "\n".join(lines)


async def technical_analysis_node(state: AgentState) -> AgentState:
    """Obtiene SMAs de 25 y 200 períodos y genera análisis técnico con LLM.

    Contract:
    - Input: estado con opcional `symbols` (usa el primero).
    - Output: mismo estado, agregando:
        - `technical_analysis_trend` (str): análisis de tendencia
        - `technical_analysis_crossover` (str): estado del cruce
        - `technical_analysis_momentum` (str): momentum del mercado
        - `technical_analysis_conclusion` (str): conclusión
      o `error_message` si algo falla.

    Regla LangGraph: siempre devolver el mismo objeto/Tipo de estado.
    """

    # Defaults razonables
    symbols = state.get("symbols") or ["BTCUSD"]
    # Tomamos el primer símbolo, formato Polygon requiere "X:BTCUSD"
    symbol = symbols[0] if symbols else "BTCUSD"
    if not symbol.startswith("X:"):
        symbol = f"X:{symbol}"

    logger.info(f"Obteniendo análisis técnico para {symbol}")

    # Obtener SMA de 25 períodos (últimos 10 valores)
    try:
        sma_25_response = await sma_client.get_sma(
            symbol=symbol,
            timespan="day",
            window=25,
            series_type="close",
            order="desc",
            limit=10,
        )
    except IndicatorClientError as exc:
        logger.error("Error obteniendo SMA 25: %s", str(exc), exc_info=True)
        state["error_message"] = f"Error obteniendo SMA 25: {str(exc)}"
        return state

    # Obtener SMA de 200 períodos (últimos 10 valores)
    try:
        sma_200_response = await sma_client.get_sma(
            symbol=symbol,
            timespan="day",
            window=200,
            series_type="close",
            order="desc",
            limit=10,
        )
    except IndicatorClientError as exc:
        logger.error("Error obteniendo SMA 200: %s", str(exc), exc_info=True)
        state["error_message"] = f"Error obteniendo SMA 200: {str(exc)}"
        return state

    # Convertir valores a formato legible
    sma_25_values = [
        (datetime.fromtimestamp(v.timestamp / 1000), v.value)
        for v in sma_25_response.results.values
    ]
    sma_200_values = [
        (datetime.fromtimestamp(v.timestamp / 1000), v.value)
        for v in sma_200_response.results.values
    ]

    if not sma_25_values or not sma_200_values:
        state["error_message"] = "No se obtuvieron suficientes datos de SMAs"
        return state

    prompt_data = _format_sma_values_for_prompt(
        sma_25_values=sma_25_values, sma_200_values=sma_200_values
    )

    system_prompt = (
        "Eres un analista técnico experto en trading de criptomonedas.\n"
        "Analizarás los últimos 10 valores de las medias móviles simples (SMA) de 25 y 200 períodos.\n\n"
        "Tu tarea:\n"
        "1) Analizar la tendencia observada (3-5 frases).\n"
        "2) Identificar el estado del cruce entre SMA 25 y SMA 200:\n"
        "   - golden_cross: SMA25 por encima de SMA200 (alcista)\n"
        "   - death_cross: SMA25 por debajo de SMA200 (bajista)\n"
        "   - neutral: sin señal clara\n"
        "   - approaching: acercándose a un cruce\n"
        "3) Determinar el momentum: bullish, bearish o sideways.\n"
        "4) Dar una conclusión breve (2-3 frases) sobre qué esperar.\n\n"
        "Devuelve SOLO un JSON con las claves: trend_analysis, crossover_status, market_momentum, conclusion.\n"
        "Ejemplo:\n"
        '{"trend_analysis": "...","crossover_status": "golden_cross","market_momentum": "bullish","conclusion": "..."}'
    )

    user_prompt = f"Datos técnicos del símbolo {symbol}:\n\n{prompt_data}\n\nAnaliza y devuelve JSON."

    try:
        analysis = await agent_executor.execute(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            response_model=TechnicalAnalysis,
            context={"symbol": symbol, "node": "technical_analysis"},
        )
    except AgentExecutorError as exc:
        logger.error("Error ejecutando análisis técnico: %s", str(exc), exc_info=True)
        state["error_message"] = f"Error en análisis técnico: {str(exc)}"
        return state

    # Asignar resultados validados al estado
    state["technical_analysis_trend"] = analysis.trend_analysis
    state["technical_analysis_crossover"] = analysis.crossover_status
    state["technical_analysis_momentum"] = analysis.market_momentum
    state["technical_analysis_conclusion"] = analysis.conclusion

    # Limpieza de error si todo fue bien
    if state.get("error_message"):
        state["error_message"] = None

    logger.info(f"Análisis técnico completado: {analysis.market_momentum} / {analysis.crossover_status}")

    return state

