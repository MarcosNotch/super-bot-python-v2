"""Modelos Pydantic para el análisis técnico de SMAs."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field


class TechnicalAnalysis(BaseModel):
    """Respuesta estructurada del LLM para análisis técnico basado en SMAs."""

    trend_analysis: str = Field(
        ...,
        min_length=20,
        description="Análisis de la tendencia observada en las SMAs (3-5 frases)",
    )
    crossover_status: Literal["golden_cross", "death_cross", "neutral", "approaching"] = Field(
        ...,
        description=(
            "Estado del cruce entre SMA 25 y SMA 200. "
            "golden_cross: SMA25 > SMA200 (alcista), "
            "death_cross: SMA25 < SMA200 (bajista), "
            "neutral: sin señal clara, "
            "approaching: acercándose a un cruce"
        ),
    )
    market_momentum: Literal["bullish", "bearish", "sideways"] = Field(
        ..., description="Momentum del mercado según el análisis técnico"
    )
    conclusion: str = Field(
        ...,
        min_length=15,
        description="Conclusión breve sobre qué esperar del mercado (2-3 frases)",
    )

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "trend_analysis": "La SMA de 25 períodos muestra una tendencia ascendente clara, mientras que la SMA de 200 se mantiene estable. El precio se encuentra por encima de ambas medias, lo que sugiere fortaleza del mercado.",
                    "crossover_status": "golden_cross",
                    "market_momentum": "bullish",
                    "conclusion": "El mercado mantiene una estructura alcista con soporte sólido. Se espera continuación de la tendencia en el corto plazo.",
                }
            ]
        }
    }

