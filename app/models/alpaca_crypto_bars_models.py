from datetime import datetime
from typing import Dict, List

from pydantic import BaseModel, Field


class AlpacaCryptoBar(BaseModel):
    """Barra de precio de cripto devuelta por Alpaca.

    Los campos siguen la convención de la API v1beta3 de Alpaca.
    """

    o: float = Field(..., description="Precio de apertura (open)")
    h: float = Field(..., description="Precio máximo (high)")
    l: float = Field(..., description="Precio mínimo (low)")
    c: float = Field(..., description="Precio de cierre (close)")
    v: float = Field(..., description="Volumen negociado")
    n: int = Field(..., description="Número de operaciones en el periodo")
    vw: float = Field(..., description="Precio medio ponderado por volumen (VWAP)")
    t: datetime = Field(..., description="Fecha/hora del bar en formato ISO 8601")

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "c": 96488.828,
                    "h": 97443.364467005,
                    "l": 94146.5695,
                    "n": 323,
                    "o": 94146.5695,
                    "t": "2025-05-01T00:00:00Z",
                    "v": 1.773802489,
                    "vw": 96283.1373735878,
                }
            ]
        }
    }


class AlpacaCryptoBarsResponse(BaseModel):
    """Respuesta principal de la API de crypto bars de Alpaca.

    El campo `bars` es un diccionario donde la clave es el símbolo (ej. "BTC/USD")
    y el valor es la lista de barras para ese símbolo.
    """

    bars: Dict[str, List[AlpacaCryptoBar]] = Field(
        ..., description="Diccionario de símbolos a lista de barras de precio"
    )

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "bars": {
                        "BTC/USD": [
                            {
                                "c": 96488.828,
                                "h": 97443.364467005,
                                "l": 94146.5695,
                                "n": 323,
                                "o": 94146.5695,
                                "t": "2025-05-01T00:00:00Z",
                                "v": 1.773802489,
                                "vw": 96283.1373735878,
                            }
                        ]
                    }
                }
            ]
        }
    }

