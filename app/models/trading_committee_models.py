"""Modelos Pydantic para el sistema Trading Committee (3 agentes)."""

from __future__ import annotations

from typing import List, Literal

from pydantic import BaseModel, Field, field_validator


class StrategistProposal(BaseModel):
    """Propuesta estructurada del Agente 1: El Estratega (The Opportunist)."""

    direction: Literal["buy", "sell", "hold"] = Field(
        ..., description="Dirección del trade propuesto"
    )
    entry_price: float = Field(..., gt=0, description="Precio de entrada sugerido")
    stop_loss: float = Field(..., gt=0, description="Stop Loss sugerido")
    take_profit: float = Field(..., gt=0, description="Take Profit sugerido")
    risk_reward_ratio: str = Field(
        ..., description="Ratio riesgo/recompensa (ej: '1:2.5')"
    )
    justification: str = Field(
        ...,
        min_length=50,
        description="Justificación completa de por qué el contexto favorece el movimiento (mínimo 50 caracteres)",
    )
    key_factors: List[str] = Field(
        ...,
        description="Lista de 2-5 factores clave que apoyan la propuesta",
    )
    confidence_level: Literal["high", "medium", "low"] = Field(
        ..., description="Nivel de confianza en la propuesta"
    )

    @field_validator("key_factors")
    @classmethod
    def validate_key_factors_length(cls, v: List[str]) -> List[str]:
        """Valida que haya entre 2 y 5 factores clave."""
        if len(v) < 2:
            raise ValueError("Debe haber al menos 2 factores clave")
        if len(v) > 5:
            raise ValueError("No debe haber más de 5 factores clave")
        return v

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "direction": "buy",
                    "justification": "El precio se encuentra en zona alta del rango de 10 días con soporte sólido en $95,000. Las noticias sobre aprobación de ETF en Hong Kong generan momentum alcista institucional. SMA muestra estructura alcista confirmada con MACD. Fear & Greed en 75 indica apetito pero aún no extremo.",
                    "key_factors": [
                        "Soporte fuerte en $95,000 (-1.5%)",
                        "Aprobación de ETF genera demanda institucional",
                        "MACD cruce alcista confirmado",
                        "Fear & Greed en 75 (Greed moderado)",
                        "Precio en zona alta del rango (oportunidad de breakout)",
                    ],
                    "confidence_level": "high",
                }
            ]
        }
    }

