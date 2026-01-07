"""Nodo: consulta el Fear & Greed Index y actualiza el estado."""

from __future__ import annotations

import logging

from app.agent.state.agent_state import AgentState
from app.clients.fear_greed_client import FearGreedClientError, fear_greed_client

logger = logging.getLogger(__name__)


async def fear_greed_node(state: AgentState) -> AgentState:
    """Consulta el Fear & Greed Index y actualiza el estado.

    Este nodo es simple: solo obtiene el valor más reciente del índice
    y lo agrega al estado sin procesamiento adicional.

    Contract:
    - Input: estado (no requiere campos específicos).
    - Output: mismo estado, agregando:
        - `fear_greed_index` (int): valor del índice (0-100)
        - `fear_greed_classification` (str): clasificación textual
      o `error_message` si algo falla.

    Regla LangGraph: siempre devolver el mismo objeto/Tipo de estado.
    """

    logger.info("Consultando Fear & Greed Index")

    try:
        response = await fear_greed_client.get_latest(limit=1)
    except FearGreedClientError as exc:
        logger.error("Error consultando Fear & Greed Index: %s", str(exc), exc_info=True)
        state["error_message"] = f"Error consultando Fear & Greed Index: {str(exc)}"
        return state

    # Validar que haya datos
    if not response.data:
        state["error_message"] = "No se obtuvieron datos del Fear & Greed Index"
        return state

    # Tomar el valor más reciente
    latest = response.data[0]

    # Actualizar estado
    state["fear_greed_index"] = latest.value
    state["fear_greed_classification"] = latest.value_classification

    # Limpieza de error si todo fue bien
    if state.get("error_message"):
        state["error_message"] = None

    logger.info(
        f"Fear & Greed Index obtenido: {latest.value} ({latest.value_classification})"
    )

    return state

