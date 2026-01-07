from typing import List, Optional

from pydantic import BaseModel, Field


class FearGreedValue(BaseModel):
    """Valor individual del índice Fear & Greed para una fecha concreta."""

    value: int = Field(..., description="Valor numérico del índice (0-100)")
    value_classification: str = Field(
        ..., description="Clasificación textual (Extreme Fear, Fear, Neutral, Greed, Extreme Greed)",
    )
    timestamp: str = Field(..., description="Timestamp en formato UNIX o ISO según la API")
    time_until_update: Optional[str] = Field(
        None,
        description="Tiempo restante hasta la próxima actualización, si está disponible",
    )

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "value": 74,
                    "value_classification": "Greed",
                    "timestamp": "1766534400",
                    "time_until_update": "86400",
                }
            ]
        }
    }


class FearGreedResponse(BaseModel):
    """Respuesta principal del índice Fear & Greed."""

    name: Optional[str] = Field(
        None, description="Nombre del índice o fuente de los datos, si se provee"
    )
    data: List[FearGreedValue] = Field(
        default_factory=list,
        description="Lista de valores del índice ordenados por fecha",
    )

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "name": "Crypto Fear and Greed Index",
                    "data": [
                        {
                            "value": 74,
                            "value_classification": "Greed",
                            "timestamp": "1766534400",
                            "time_until_update": "86400",
                        }
                    ],
                }
            ]
        }
    }

