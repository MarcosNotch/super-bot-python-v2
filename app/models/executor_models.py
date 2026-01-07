"""Modelos Pydantic para el Agente 3: El Juez de Riesgo (The Executor)."""

from __future__ import annotations

from typing import List, Literal

from pydantic import BaseModel, Field


class ExecutorDecision(BaseModel):
    """Decisión estructurada del Agente 3: El Juez de Riesgo (The Executor)."""

    final_decision: Literal["buy", "sell", "hold"] = Field(
        ...,
        description="Decisión final del Juez basada en la evaluación de ambos agentes",
    )

    reasoning: str = Field(
        ...,
        min_length=100,
        description="Razonamiento completo y equilibrado de la decisión (mínimo 100 caracteres)",
    )

    strategist_points_accepted: List[str] = Field(
        ...,
        min_length=1,
        max_length=5,
        description="Argumentos del Estratega que el Juez considera válidos (1-5)",
    )

    skeptic_points_accepted: List[str] = Field(
        ...,
        min_length=1,
        max_length=5,
        description="Argumentos del Abogado del Diablo que el Juez considera válidos (1-5)",
    )

    key_factors_for_decision: List[str] = Field(
        ...,
        min_length=2,
        max_length=5,
        description="Factores clave que llevaron a la decisión final (2-5)",
    )

    risk_assessment: Literal["low", "medium", "high"] = Field(
        ...,
        description="Evaluación del riesgo general de la operación",
    )

    confidence_level: Literal["high", "medium", "low"] = Field(
        ...,
        description="Nivel de confianza en la decisión tomada",
    )

    position_context_considered: bool = Field(
        ...,
        description="Indica si la decisión consideró la posición actual del portfolio",
    )

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "final_decision": "hold",
                    "reasoning": "Tras evaluar ambos argumentos, concluyo que aunque existe confluencia alcista según el Estratega, los riesgos identificados por el Abogado del Diablo son significativos. El Fear & Greed en 75 está peligrosamente cerca de zona de euforia. Dado que ya tenemos posición abierta, lo prudente es mantener y esperar confirmación adicional antes de agregar exposición.",
                    "strategist_points_accepted": [
                        "Golden cross confirmado en SMAs",
                        "Noticias institucionales positivas",
                        "Soporte técnico identificado correctamente",
                    ],
                    "skeptic_points_accepted": [
                        "Fear & Greed cerca de extremo es riesgo real",
                        "Precio en zona alta aumenta probabilidad de corrección",
                        "Falta de confirmación de volumen es válida",
                    ],
                    "key_factors_for_decision": [
                        "Posición ya abierta - no agregar exposición",
                        "Riesgos de corrección son tangibles",
                        "Esperar confirmación adicional es prudente",
                    ],
                    "risk_assessment": "medium",
                    "confidence_level": "high",
                    "position_context_considered": True,
                }
            ]
        }
    }

