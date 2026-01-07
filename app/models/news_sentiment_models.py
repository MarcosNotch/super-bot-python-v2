"""Modelos Pydantic para el análisis de sentimiento de noticias."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field


class NewsSentimentAnalysis(BaseModel):
    """Respuesta estructurada del LLM para análisis de sentimiento de noticias."""

    context_summary: str = Field(
        ...,
        min_length=10,
        description="Resumen del contexto general de las noticias en 3-6 frases",
    )
    market_opinion: str = Field(
        ...,
        min_length=10,
        description="Opinión breve sobre el impacto probable en el mercado cripto",
    )
    sentiment: Literal["positive", "negative"] = Field(
        ..., description="Sentimiento global clasificado"
    )

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "context_summary": "Bitcoin continúa su tendencia alcista mientras Ethereum muestra consolidación. Las noticias reflejan optimismo institucional con nuevos ETFs aprobados.",
                    "market_opinion": "El contexto es favorable para el mercado cripto en el corto plazo, con posible continuación de la tendencia alcista en los próximos días.",
                    "sentiment": "positive",
                }
            ]
        }
    }

