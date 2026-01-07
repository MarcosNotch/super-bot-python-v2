"""Schemas Pydantic para el controller de trading."""

from __future__ import annotations

from typing import List, Optional

from pydantic import BaseModel, Field


class TradingAnalysisRequest(BaseModel):
    """Request para iniciar análisis de trading."""

    symbols: List[str] = Field(
        ...,
        min_length=1,
        max_length=5,
        description="Lista de símbolos a analizar (ej: ['BTCUSD'])",
    )
    news_limit: int = Field(
        default=10,
        ge=1,
        le=50,
        description="Número de noticias a analizar",
    )

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "symbols": ["BTCUSD"],
                    "news_limit": 10,
                }
            ]
        }
    }


class NewsAnalysisResult(BaseModel):
    """Resultado del análisis de noticias."""

    sentiment: Optional[str] = None
    context_summary: Optional[str] = None
    market_opinion: Optional[str] = None


class TechnicalAnalysisResult(BaseModel):
    """Resultado del análisis técnico."""

    trend_analysis: Optional[str] = None
    crossover_status: Optional[str] = None
    momentum: Optional[str] = None
    conclusion: Optional[str] = None


class FearGreedResult(BaseModel):
    """Resultado del Fear & Greed Index."""

    index: Optional[int] = None
    classification: Optional[str] = None


class SupportResistanceResult(BaseModel):
    """Resultado del análisis de soporte/resistencia."""

    nearest_support: Optional[float] = None
    distance_to_support: Optional[str] = None
    nearest_resistance: Optional[float] = None
    distance_to_resistance: Optional[str] = None


class StrategistProposalResult(BaseModel):
    """Resultado de la propuesta del Estratega."""

    direction: Optional[str] = None
    entry_price: Optional[float] = None
    stop_loss: Optional[float] = None
    take_profit: Optional[float] = None
    risk_reward_ratio: Optional[str] = None
    justification: Optional[str] = None
    proposal_text: Optional[str] = None


class TradingAnalysisResponse(BaseModel):
    """Response completa del análisis de trading."""

    success: bool = Field(..., description="Indica si el análisis se completó exitosamente")
    symbols: List[str] = Field(..., description="Símbolos analizados")
    error_message: Optional[str] = Field(None, description="Mensaje de error si falló")

    # Resultados de análisis
    news_analysis: Optional[NewsAnalysisResult] = None
    technical_analysis: Optional[TechnicalAnalysisResult] = None
    fear_greed: Optional[FearGreedResult] = None
    support_resistance: Optional[SupportResistanceResult] = None
    strategist_proposal: Optional[StrategistProposalResult] = None

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "success": True,
                    "symbols": ["BTCUSD"],
                    "error_message": None,
                    "news_analysis": {
                        "sentiment": "positive",
                        "context_summary": "Aprobación de ETF impulsa demanda...",
                        "market_opinion": "Contexto favorable para alcistas...",
                    },
                    "technical_analysis": {
                        "trend_analysis": "SMA 25 > SMA 200, tendencia alcista",
                        "crossover_status": "golden_cross",
                        "momentum": "bullish",
                        "conclusion": "Estructura alcista confirmada",
                    },
                    "fear_greed": {"index": 75, "classification": "Greed"},
                    "support_resistance": {
                        "nearest_support": 95000.0,
                        "distance_to_support": "-1.5%",
                        "nearest_resistance": 98000.0,
                        "distance_to_resistance": "+1.5%",
                    },
                    "strategist_proposal": {
                        "direction": "buy",
                        "justification": "Confluencia de señales alcistas...",
                    },
                    "skeptic_critique": {
                        "overall_assessment": "proceed_with_caution",
                        "critique_text": "Si bien hay señales alcistas, existen riesgos...",
                        "identified_risks": [
                            "Fear & Greed cerca de zona extrema",
                            "Precio en zona alta del rango",
                            "Posible trampa alcista",
                        ],
                    },
                    "executor_decision": {
                        "final_decision": "hold",
                        "reasoning": "Considerando ambos argumentos y la posición actual...",
                        "risk_assessment": "medium",
                        "confidence_level": "high",
                        "has_current_position": True,
                    },
                }
            ]
        }
    }


