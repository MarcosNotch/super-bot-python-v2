"""Nodo: obtiene las últimas noticias y genera resumen + sentimiento con LLM."""

from __future__ import annotations

import logging
from typing import List

from app.agent.state.agent_state import AgentState
from app.clients.alpaca_news_client import AlpacaNewsClientError, alpaca_news_client
from app.models.news_sentiment_models import NewsSentimentAnalysis
from app.utils.agent_executor import AgentExecutorError, agent_executor

logger = logging.getLogger(__name__)


def _format_news_items_for_prompt(*, headlines: List[str]) -> str:
    """Formatea titulares para el prompt del LLM.

    Args:
        headlines: Lista de titulares.

    Returns:
        str: Texto listo para el prompt.
    """

    if not headlines:
        return "(sin noticias)"

    lines = [f"- {h.strip()}" for h in headlines if h and h.strip()]
    return "\n".join(lines) if lines else "(sin noticias)"


async def crypto_news_sentiment_node(state: AgentState) -> AgentState:
    """Trae las últimas N noticias y genera contexto + opinión de mercado.

    Contract:
    - Input: estado con opcional `symbols` y `news_limit`.
    - Output: mismo estado, agregando:
        - `news_context_summary`
        - `news_market_opinion`
        - `news_sentiment` (positive/negative/mixed/neutral)
      o `error_message` si algo falla.

    Regla LangGraph: siempre devolver el mismo objeto/Tipo de estado.
    """

    # Defaults razonables
    symbols = state.get("symbols") or ["BTCUSD", "ETHUSD"]
    limit = int(state.get("news_limit") or 10)
    limit = max(1, min(limit, 50))

    try:
        news_response = await alpaca_news_client.get_news(
            symbols=symbols,
            limit=limit,
            include_content=True,
        )
    except AlpacaNewsClientError as exc:
        logger.error("No se pudieron obtener noticias de Alpaca: %s", str(exc), exc_info=True)
        state["error_message"] = f"Error obteniendo noticias: {str(exc)}"
        return state

    headlines = [
        item.headline if item.headline else (item.summary or "") for item in news_response.news
    ]

    prompt_news = _format_news_items_for_prompt(headlines=headlines)

    system_prompt = (
        "Eres un analista de mercados cripto experto.\n"
        "Dado un conjunto de titulares recientes, debes:\n"
        "1) Resumir el contexto general en 3-6 frases.\n"
        "2) Dar una opinión breve sobre el impacto probable en el mercado cripto.\n"
        "3) Clasificar el sentimiento global como: positive, negative, mixed o neutral.\n\n"
        "Devuelve SOLO un JSON con las claves: context_summary, market_opinion, sentiment.\n"
        "Ejemplo:\n"
        '{"context_summary": "Bitcoin sube...","market_opinion": "Favorable...","sentiment": "positive"}'
    )

    user_prompt = f"Titulares recientes ({limit} noticias):\n{prompt_news}\n\nAnaliza y devuelve JSON."

    try:
        analysis = await agent_executor.execute(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            response_model=NewsSentimentAnalysis,
            context={"symbols": symbols, "limit": limit},
        )
    except AgentExecutorError as exc:
        logger.error("Error ejecutando análisis de noticias: %s", str(exc), exc_info=True)
        state["error_message"] = f"Error en análisis de noticias: {str(exc)}"
        return state

    # Asignar resultados validados al estado
    state["news_context_summary"] = analysis.context_summary
    state["news_market_opinion"] = analysis.market_opinion
    state["news_sentiment"] = analysis.sentiment

    # Limpieza de error si todo fue bien
    if state.get("error_message"):
        state["error_message"] = None

    return state

