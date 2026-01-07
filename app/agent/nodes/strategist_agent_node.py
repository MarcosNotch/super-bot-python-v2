"""Nodo: Agente 1 - El Estratega (The Opportunist).

Este agente es optimista por diseño pero basado en datos.
Su misión es encontrar razones para entrar al mercado cuando hay alineación.
"""

from __future__ import annotations

import logging
from typing import Dict

from app.agent.state.agent_state import AgentState
from app.database import AsyncSessionLocal, TransactionRepository
from app.models.trading_committee_models import StrategistProposal
from app.utils.agent_executor import AgentExecutorError, agent_executor

logger = logging.getLogger(__name__)


async def _get_current_position_context(symbol: str) -> Dict[str, any]:
    """Obtiene el contexto de la posición actual del portfolio.

    Args:
        symbol: Símbolo del activo.

    Returns:
        Diccionario con información de posición y balance.
    """
    async with AsyncSessionLocal() as session:
        repo = TransactionRepository(session)

        # Obtener posición actual
        quantity = await repo.get_position_quantity(symbol)

        # Obtener balance disponible
        available_usd = await repo.get_available_balance()

        # Obtener precio promedio si hay posición
        avg_buy_price = None
        if quantity > 0:
            avg_buy_price = await repo.get_average_buy_price(symbol)

        return {
            "has_position": quantity > 0,
            "current_quantity": quantity,
            "average_buy_price": avg_buy_price,
            "available_usd": available_usd,
            "can_buy": available_usd > 0,
            "can_sell": quantity > 0,
        }

def _build_position_context_text(position: Dict[str, any], symbol: str) -> str:
    """Construye texto legible sobre la posición actual.

    Args:
        position: Diccionario con datos de posición.
        symbol: Símbolo del activo.

    Returns:
        str: Texto formateado.
    """
    if position["has_position"]:
        return f"""
=== POSICIÓN ACTUAL EN {symbol} ===

✅ TIENES POSICIÓN ABIERTA
  • Cantidad: {position['current_quantity']:.8f}
  • Precio promedio de compra: ${position['average_buy_price']:,.2f}
  • Valor estimado: ${position['current_quantity'] * position['average_buy_price']:,.2f}

💵 Balance disponible: ${position['available_usd']:,.2f} USD

ACCIONES DISPONIBLES:
  • SELL - Puedes cerrar la posición
  • HOLD - Mantener la posición actual
"""
    else:
        return f"""
=== POSICIÓN ACTUAL EN {symbol} ===

⚪ NO TIENES POSICIÓN ABIERTA
  • Cantidad: 0
  • Sin exposición al activo

💵 Balance disponible: ${position['available_usd']:,.2f} USD

ACCIONES DISPONIBLES:
  • BUY - Puedes abrir posición si el análisis es favorable
  • HOLD - Esperar mejor oportunidad
"""


async def _build_market_context(state: AgentState) -> Dict[str, any]:
    """Construye el contexto de mercado desde el estado.

    Args:
        state: Estado del agente con todos los datos recopilados.

    Returns:
        Diccionario con el contexto estructurado para el prompt.
    """
    # Extraer datos del estado
    symbol = state.get("symbols", ["BTCUSD"])[0]
    current_price = state.get("current_price")

    position_context = await _get_current_position_context(symbol)

    # Price context
    price_context = {
        "current_price": current_price,
        "nearest_support": state.get("nearest_support"),
        "distance_to_support": state.get("distance_to_support"),
        "nearest_resistance": state.get("nearest_resistance"),
        "distance_to_resistance": state.get("distance_to_resistance"),
    }

    # Technical analysis
    technical = {
        "trend_analysis": state.get("technical_analysis_trend"),
        "crossover_status": state.get("technical_analysis_crossover"),
        "momentum": state.get("technical_analysis_momentum"),
        "conclusion": state.get("technical_analysis_conclusion"),
    }

    # News sentiment
    news = {
        "sentiment": state.get("news_sentiment"),
        "context_summary": state.get("news_context_summary"),
        "market_opinion": state.get("news_market_opinion"),
    }

    # Fear & Greed
    fear_greed = {
        "index": state.get("fear_greed_index"),
        "classification": state.get("fear_greed_classification"),
    }

    return {
        "symbol": symbol,
        "price_context": price_context,
        "technical_analysis": technical,
        "news_sentiment": news,
        "fear_greed": fear_greed,
        "position": position_context,
    }


def _format_context_for_prompt(context: Dict[str, any]) -> str:
    """Formatea el contexto de mercado para el prompt del LLM.

    Args:
        context: Diccionario con el contexto de mercado.

    Returns:
        str: Texto formateado para el prompt.
    """
    # Construir información de posición
    position = context.get("position", {})
    position_text = _build_position_context_text(position, context['symbol'])

    lines = [
        f"=== CONTEXTO DE MERCADO: {context['symbol']} ===",
        "",
        position_text,
        "📊 PRECIO Y NIVELES:",
        f"  • Precio actual: ${context['price_context']['current_price']:,.2f}",
        f"  • Soporte más cercano: ${context['price_context']['nearest_support']:,.2f} ({context['price_context']['distance_to_support']})",
        f"  • Resistencia más cercana: ${context['price_context']['nearest_resistance']:,.2f} ({context['price_context']['distance_to_resistance']})",
        "",
        "📈 ANÁLISIS TÉCNICO:",
        f"  • Tendencia: {context['technical_analysis']['trend_analysis'] or 'N/A'}",
        f"  • Estado de cruce (SMA 25/200): {context['technical_analysis']['crossover_status'] or 'N/A'}",
        f"  • Momentum: {context['technical_analysis']['momentum'] or 'N/A'}",
        f"  • Conclusión técnica: {context['technical_analysis']['conclusion'] or 'N/A'}",
        "",
        "📰 SENTIMIENTO DE NOTICIAS:",
        f"  • Sentimiento general: {context['news_sentiment']['sentiment'] or 'N/A'}",
        f"  • Contexto: {context['news_sentiment']['context_summary'] or 'N/A'}",
        f"  • Opinión de mercado: {context['news_sentiment']['market_opinion'] or 'N/A'}",
        "",
        "😨 FEAR & GREED INDEX:",
        f"  • Índice: {context['fear_greed']['index'] or 'N/A'}/100",
        f"  • Clasificación: {context['fear_greed']['classification'] or 'N/A'}",
    ]

    return "\n".join(lines)


async def strategist_agent_node(state: AgentState) -> AgentState:
    """Agente 1: El Estratega (The Opportunist).

    Analiza el contexto completo del mercado y propone un trade si encuentra
    alineación entre los factores técnicos, fundamentales y de sentimiento.

    Es optimista por diseño pero basado en datos.

    Contract:
    - Input: estado con datos de análisis técnico, noticias, F&G y S/R.
    - Output: mismo estado, agregando:
        - `strategist_proposal` (str): propuesta completa
        - `strategist_direction` (str): "buy" | "sell" | "hold"
        - `strategist_entry_price` (float)
        - `strategist_stop_loss` (float)
        - `strategist_take_profit` (float)
        - `strategist_justification` (str)
        - `strategist_risk_reward_ratio` (str)
      o `error_message` si algo falla.

    Regla LangGraph: siempre devolver el mismo objeto/Tipo de estado.
    """

    logger.info("🎯 Agente 1 (El Estratega) iniciando análisis...")

    # 1. Construir contexto de mercado (obtiene precio actual real)
    context = await _build_market_context(state)
    formatted_context = _format_context_for_prompt(context)

    # 2. Crear prompt para el LLM
    system_prompt = """Eres "El Estratega" (The Opportunist), el Agente 1 del Trading Committee.

TU PERSONALIDAD:
- Eres OPTIMISTA por diseño, pero basado en datos
- Tu misión es ENCONTRAR razones para entrar al mercado
- Buscas ALINEACIÓN entre factores técnicos, fundamentales y sentimiento
- Eres PROACTIVO y propones trades cuando ves oportunidad

TU TRABAJO:
1. Analizar el contexto completo del mercado
2. Considerar tu POSICIÓN ACTUAL (si ya tienes o no exposición)
3. Buscar CONFLUENCIA de señales alcistas o bajistas
4. Si encuentras alineación, proponer una DIRECCIÓN de trade (buy/sell/hold) con:
   - Dirección (buy/sell/hold)
   - Justificación clara de POR QUÉ el contexto favorece el movimiento
   - Factores clave que apoyan tu propuesta (2-5 factores)
   - Nivel de confianza (high/medium/low)

REGLAS SOBRE POSICIÓN ACTUAL:
- Si YA TIENES posición abierta → Considera si mantener (hold) o vender (sell)
- Si NO tienes posición → Puedes proponer buy si el análisis es favorable
- Si tienes posición y el contexto es alcista → Considera hold (ya estás expuesto)
- Si tienes posición y el contexto es bajista → Considera sell
- Si NO tienes posición y el contexto es alcista → Considera buy

REGLAS DE ANÁLISIS:
- Si el precio está en un soporte Y las noticias son positivas → BUSCA razón para comprar (si no tienes posición)
- Si el precio está en resistencia Y las noticias son negativas → BUSCA razón para vender (si tienes posición)
- Si Fear & Greed < 30 (Extreme Fear) → Oportunidad de compra contrarian
- Si Fear & Greed > 80 (Extreme Greed) → Oportunidad de venta contrarian
- Si NO hay confluencia clara → direction: "hold"

IMPORTANTE:
- Considera SIEMPRE tu posición actual en la decisión
- Sé específico en tu justificación
- Menciona los factores más relevantes que apoyan tu decisión
- Explica el contexto general del mercado

Devuelve SOLO un JSON con el formato especificado."""

    user_prompt = f"""Analiza el siguiente contexto de mercado y propone un trade:

{formatted_context}

Recuerda: Eres OPTIMISTA y buscas oportunidades.
"""

    # 4. Ejecutar con AgentExecutor
    try:
        proposal = await agent_executor.execute(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            response_model=StrategistProposal,
            context={"agent": "strategist", "symbol": context["symbol"]},
        )
    except AgentExecutorError as exc:
        logger.error(f"Error ejecutando Agente Estratega: {exc}", exc_info=True)
        state["error_message"] = f"Error en Agente Estratega: {str(exc)}"
        return state

    # 5. Asignar resultados al estado
    state["strategist_direction"] = proposal.direction
    state["strategist_justification"] = proposal.justification

    # Construir propuesta completa en texto
    key_factors_text = "\n".join([f"  • {factor}" for factor in proposal.key_factors])
    state["strategist_proposal"] = f"""
📋 PROPUESTA DEL ESTRATEGA

Dirección: {proposal.direction.upper()}
Confianza: {proposal.confidence_level.upper()}

Justificación:
{proposal.justification}

Factores Clave:
{key_factors_text}
"""

    # Limpieza de error si todo fue bien
    if state.get("error_message"):
        state["error_message"] = None

    logger.info(
        f"✅ Agente Estratega completado: {proposal.direction.upper()} (confianza: {proposal.confidence_level})"
    )

    return state

