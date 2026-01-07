"""Estado general del agente de trading cripto.

Este estado es compartido por todos los nodos del grafo.
Regla importante: los nodos deben recibir y devolver el mismo tipo de estado.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional, TypedDict

class AgentState(TypedDict, total=False):
    """Estado general del agente de trading cripto.

    Usado por todos los nodos del grafo (noticias, análisis técnico, decisiones, etc.).
    """

    # Input general
    symbols: List[str]

    # Noticias
    news_limit: int
    news_context_summary: Optional[str]
    news_market_opinion: Optional[str]
    news_sentiment: Optional[str]  # "positive" | "negative" | "mixed" | "neutral"

    # Análisis técnico (SMAs)
    technical_analysis_trend: Optional[str]
    technical_analysis_crossover: Optional[str]  # "golden_cross" | "death_cross" | "neutral" | "approaching"
    technical_analysis_momentum: Optional[str]  # "bullish" | "bearish" | "sideways"
    technical_analysis_conclusion: Optional[str]

    # Análisis técnico (para otros futuros nodos/indicadores)
    technical_indicators: Optional[Dict[str, Any]]

    # Fear & Greed
    fear_greed_index: Optional[int]
    fear_greed_classification: Optional[str]  # "Extreme Fear" | "Fear" | "Neutral" | "Greed" | "Extreme Greed"

    # Support & Resistance (desde base de datos)
    current_price: Optional[float]  # Precio actual del activo
    nearest_support: Optional[float]
    distance_to_support: Optional[str]  # Porcentaje, ej: "-1.5%"
    nearest_resistance: Optional[float]
    distance_to_resistance: Optional[str]  # Porcentaje, ej: "+1.5%"

    # Trading Committee System (3 agentes)
    # Agente 1: El Estratega (The Opportunist)
    strategist_proposal: Optional[str]  # Propuesta completa en texto
    strategist_direction: Optional[str]  # "buy" | "sell" | "hold"
    strategist_justification: Optional[str]

    # Agente 2: El Abogado del Diablo (The Skeptic)
    skeptic_critique: Optional[str]  # Crítica completa
    skeptic_risks: Optional[List[str]]  # Lista de riesgos identificados
    skeptic_recommendation: Optional[str]  # "reject" | "proceed_with_caution"

    # Agente 3: El Juez (The Executor)
    executor_decision: Optional[str]  # "buy" | "sell" | "hold"
    executor_final_params: Optional[Dict[str, any]]  # Parámetros finales
    executor_reasoning: Optional[str]  # Razonamiento de la decisión
    executor_decision_text: Optional[str]  # Texto completo de la decisión

    # Decisión de trading (para futuros nodos)
    trading_decision: Optional[str]  # "buy" | "sell" | "hold"
    trading_confidence: Optional[float]

    # Errores
    error_message: Optional[str]



