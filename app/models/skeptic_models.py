"""Modelos Pydantic para el Agente 2: El Abogado del Diablo (The Skeptic)."""

from __future__ import annotations

from typing import List, Literal

from pydantic import BaseModel, Field, field_validator


class SkepticCritique(BaseModel):
    """Crítica estructurada del Agente 2: El Abogado del Diablo (The Skeptic)."""

    overall_assessment: Literal["reject", "proceed_with_caution", "acceptable"] = Field(
        ...,
        description="Evaluación general de la propuesta del Estratega",
    )

    main_critique: str = Field(
        ...,
        min_length=100,
        description="Crítica principal y mordaz de la propuesta (mínimo 100 caracteres)",
    )

    identified_risks: List[str] = Field(
        ...,
        description="Lista de 3-7 riesgos específicos identificados",
    )

    contradictions: List[str] = Field(
        default_factory=list,
        description="Contradicciones encontradas en el análisis del Estratega",
    )

    missing_considerations: List[str] = Field(
        default_factory=list,
        description="Factores importantes que el Estratega ignoró o minimizó",
    )

    recommendation: str = Field(
        ...,
        min_length=50,
        description="Recomendación final del Abogado del Diablo",
    )

    @field_validator("identified_risks")
    @classmethod
    def validate_risks_length(cls, v: List[str]) -> List[str]:
        """Valida que haya entre 3 y 7 riesgos identificados."""
        if len(v) < 3:
            raise ValueError("Debe haber al menos 3 riesgos identificados")
        if len(v) > 7:
            raise ValueError("No debe haber más de 7 riesgos identificados")
        return v

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "overall_assessment": "proceed_with_caution",
                    "main_critique": "Si bien el Estratega identifica confluencia alcista, hay señales contradictorias que ignora deliberadamente. El Fear & Greed en 75 está peligrosamente cerca de zona de Extreme Greed, lo que históricamente precede correcciones. El momentum alcista puede ser una trampa de liquidez.",
                    "identified_risks": [
                        "Fear & Greed en 75 cerca de Extreme Greed (>80)",
                        "Precio en zona alta del rango - riesgo de reversión",
                        "Posible trampa alcista antes de corrección",
                        "Falta de confirmación de volumen en el análisis",
                        "Sesgo de confirmación en interpretación de noticias",
                    ],
                    "contradictions": [
                        "El Estratega dice que F&G 75 es 'moderado' pero está cerca del extremo",
                        "Ignora que estar en zona alta del rango es señal de riesgo, no oportunidad",
                    ],
                    "missing_considerations": [
                        "No considera el contexto macroeconómico global",
                        "Ignora que las noticias positivas pueden estar descontadas",
                        "No evalúa el sentimiento contrarian",
                    ],
                    "recommendation": "Proceder con extrema cautela. Si se ejecuta, usar posición reducida y estar preparado para salida rápida ante cualquier señal de reversión.",
                }
            ]
        }
    }

