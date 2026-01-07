"""Configuración del grafo de LangGraph para el sistema de trading.

Este grafo orquesta todos los nodos de análisis y el Trading Committee
para tomar decisiones de trading informadas.
"""

from __future__ import annotations

import logging
from typing import Dict, List, Literal

from langgraph.graph import END, START, StateGraph

from app.agent import skeptic_agent_node, executor_agent_node
from app.agent.nodes import (
    crypto_news_sentiment_node,
    fear_greed_node,
    strategist_agent_node,
    support_resistance_node,
    technical_analysis_node,
)
from app.agent.state.agent_state import AgentState

logger = logging.getLogger(__name__)


def should_continue_to_strategist(state: AgentState) -> Literal["strategist", "end"]:
    """Decide si continuar al Estratega o terminar.

    Verifica que los nodos de análisis hayan completado exitosamente.

    Args:
        state: Estado del agente.

    Returns:
        "strategist" si se puede continuar, "end" si hay errores.
    """
    # Si hay error crítico, terminar
    if state.get("error_message"):
        logger.error(f"Error crítico detectado: {state['error_message']}")
        return "end"

    # Verificar que tenemos datos mínimos necesarios
    required_fields = [
        "news_sentiment",
        "technical_analysis_momentum",
        "fear_greed_index",
        "nearest_support",
        "nearest_resistance",
    ]

    missing_fields = [field for field in required_fields if not state.get(field)]

    if missing_fields:
        logger.warning(f"Campos faltantes para el Estratega: {missing_fields}")
        state["error_message"] = f"Datos incompletos: faltan {', '.join(missing_fields)}"
        return "end"

    return "strategist"


def build_trading_graph() -> StateGraph:
    """Construye el grafo de LangGraph para el sistema de trading.

    Flujo del grafo (SECUENCIAL para evitar conflictos de concurrencia):
    1. START → Noticias
    2. Noticias → Análisis Técnico
    3. Análisis Técnico → Fear & Greed
    4. Fear & Greed → Soporte/Resistencia
    5. Soporte/Resistencia → Estratega
    6. Estratega → END

    Returns:
        StateGraph compilado y listo para ejecutar.
    """
    # Crear grafo con el estado tipado
    graph = StateGraph(AgentState)

    # ===== FASE 1: ANÁLISIS DE MERCADO (Secuencial) =====

    graph.add_node("news_analysis", crypto_news_sentiment_node)
    graph.add_node("technical_analysis", technical_analysis_node)
    graph.add_node("fear_greed_analysis", fear_greed_node)
    graph.add_node("support_resistance_analysis", support_resistance_node)

    # ===== FASE 2: TRADING COMMITTEE =====

    # Agente 1: El Estratega
    graph.add_node("strategist", strategist_agent_node)

    # TODO: Agente 2: El Abogado del Diablo
    graph.add_node("skeptic", skeptic_agent_node)

    # TODO: Agente 3: El Juez
    graph.add_node("executor", executor_agent_node)

    # ===== FLUJO DEL GRAFO (SECUENCIAL) =====

    # START → Noticias
    graph.add_edge(START, "news_analysis")

    # Noticias → Análisis Técnico
    graph.add_edge("news_analysis", "technical_analysis")

    # Análisis Técnico → Fear & Greed
    graph.add_edge("technical_analysis", "fear_greed_analysis")

    # Fear & Greed → Soporte/Resistencia
    graph.add_edge("fear_greed_analysis", "support_resistance_analysis")

    # Soporte/Resistencia → Estratega
    graph.add_edge("support_resistance_analysis", "strategist")

    # Estratega → END
    graph.add_edge("strategist", END)

    # TODO: Cuando se implementen los otros agentes:
    graph.add_edge("strategist", "skeptic")
    graph.add_edge("skeptic", "executor")
    #graph.add_conditional_edges(
    #    "executor",
    #    should_execute_trade,
    #    {
    #        "execute": "execute_trade_node",
    #        "reject": END,
    #    }
    #)

    # Compilar el grafo
    compiled_graph = graph.compile()

    logger.info("Grafo de trading compilado exitosamente (modo SECUENCIAL)")
    return compiled_graph


# Instancia singleton del grafo compilado
trading_graph = build_trading_graph()


async def run_trading_analysis(
    symbols: List[str],
    news_limit: int = 10,
) -> AgentState:
    """Ejecuta el flujo completo de análisis de trading.

    Args:
        symbols: Lista de símbolos a analizar (ej: ["BTCUSD"]).
        news_limit: Límite de noticias a analizar.

    Returns:
        AgentState final con todos los análisis y decisiones.
    """
    # Estado inicial
    initial_state: AgentState = {
        "symbols": symbols,
        "news_limit": news_limit,
    }

    logger.info(f"Iniciando análisis de trading para {symbols}")

    # Ejecutar el grafo
    final_state = await trading_graph.ainvoke(initial_state)

    logger.info("Análisis de trading completado")

    return final_state


