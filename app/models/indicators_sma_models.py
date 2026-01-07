from typing import List, Optional

from pydantic import BaseModel, Field, HttpUrl


class IndicatorValue(BaseModel):
    """Valor individual de un indicador técnico en un timestamp concreto."""

    timestamp: int = Field(
        ..., description="Timestamp en milisegundos (epoch ms) asociado al valor calculado"
    )
    value: float = Field(..., description="Valor calculado del indicador (por ejemplo, SMA)")

    model_config = {
        "json_schema_extra": {
            "examples": [
                {"timestamp": 1766534400000, "value": 107716.27114999991}
            ]
        }
    }


class IndicatorUnderlying(BaseModel):
    """Información sobre la serie subyacente usada para el cálculo del indicador."""

    url: HttpUrl = Field(
        ..., description="URL de la serie de datos subyacente usada para el cálculo"
    )


class IndicatorResults(BaseModel):
    """Resultados de un indicador técnico (como una media móvil simple)."""

    underlying: IndicatorUnderlying = Field(
        ..., description="Información de la serie subyacente utilizada"
    )
    values: List[IndicatorValue] = Field(
        default_factory=list,
        description="Lista de valores calculados del indicador",
    )

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "underlying": {
                        "url": "https://api.polygon.io/v2/aggs/ticker/X:BTCUSD/range/1/day/1483246800000/1766696751877?limit=894&sort=desc"
                    },
                    "values": [
                        {"timestamp": 1766534400000, "value": 107716.27114999991}
                    ],
                }
            ]
        }
    }


class IndicatorResponse(BaseModel):
    """Respuesta principal de una consulta de indicador técnico (por ejemplo, SMA)."""

    results: IndicatorResults = Field(..., description="Resultados del indicador")
    status: str = Field(..., description="Estado de la respuesta (ej. 'OK')")
    request_id: Optional[str] = Field(None, description="Identificador de la petición")
    next_url: Optional[HttpUrl] = Field(
        None,
        description="URL para obtener la siguiente página de resultados, si existe",
    )

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "results": {
                        "underlying": {
                            "url": "https://api.polygon.io/v2/aggs/ticker/X:BTCUSD/range/1/day/1483246800000/1766696751877?limit=894&sort=desc"
                        },
                        "values": [
                            {
                                "timestamp": 1766534400000,
                                "value": 107716.27114999991,
                            }
                        ],
                    },
                    "status": "OK",
                    "request_id": "a16d479046da5eb609d9f698453ea6e2",
                    "next_url": "https://api.polygon.io/v1/indicators/sma/X:BTCUSD?cursor=...",
                }
            ]
        }
    }

