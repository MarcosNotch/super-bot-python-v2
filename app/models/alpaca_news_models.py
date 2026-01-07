from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field, HttpUrl


class AlpacaNewsImage(BaseModel):
    """Imagen asociada a una noticia de Alpaca."""

    size: str = Field(..., description="Tamaño de la imagen (large, small, thumb, etc.)")
    url: HttpUrl = Field(..., description="URL de la imagen")


class AlpacaNewsItem(BaseModel):
    """Elemento individual de noticia devuelto por la API de Alpaca."""

    id: int = Field(..., description="Identificador único de la noticia")
    author: Optional[str] = Field(None, description="Autor de la noticia")
    content: Optional[str] = Field(None, description="Contenido completo de la noticia, si está disponible")
    created_at: datetime = Field(..., description="Fecha de creación de la noticia")
    updated_at: Optional[datetime] = Field(None, description="Fecha de última actualización de la noticia")
    headline: str = Field(..., description="Titular de la noticia")
    source: Optional[str] = Field(None, description="Fuente de la noticia")
    summary: Optional[str] = Field(None, description="Resumen de la noticia")
    symbols: List[str] = Field(default_factory=list, description="Símbolos relacionados con la noticia")
    url: Optional[HttpUrl] = Field(None, description="URL pública de la noticia")
    images: List[AlpacaNewsImage] = Field(
        default_factory=list, description="Listado de imágenes asociadas a la noticia"
    )

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "id": 47929778,
                    "author": "Benzinga Newsdesk",
                    "content": "",
                    "created_at": "2025-09-29T20:40:00Z",
                    "updated_at": "2025-09-29T20:40:01Z",
                    "headline": "Eric Trump Declares Bitcoin 'The Future' As Shorts Get Liquidated For $83 Million",
                    "source": "benzinga",
                    "summary": "Bitcoin (CRYPTO: BTC) has surged above $114,000...",
                    "symbols": ["ABTC", "BTCUSD"],
                    "url": "https://www.benzinga.com/crypto/cryptocurrency/25/09/47929778/eric-trump-declares-bitcoin-the-future-as-shorts-get-liquidated-for-83-million",
                    "images": [
                        {
                            "size": "large",
                            "url": "https://cdn.benzinga.com/files/imagecache/2048x1536xUP/images/story/2025/09/29/Eric-Trump_0.jpeg",
                        }
                    ],
                }
            ]
        },
        "extra": "ignore",
    }


class AlpacaNewsResponse(BaseModel):
    """Respuesta principal de la API de noticias de Alpaca."""

    news: List[AlpacaNewsItem] = Field(
        default_factory=list, description="Listado de noticias devueltas por la API"
    )
    next_page_token: Optional[str] = Field(
        None, description="Token para paginar y obtener la siguiente página de resultados"
    )

    model_config = {
        "extra": "ignore",
        "json_schema_extra": {
            "examples": [
                {
                    "news": [
                        {
                            "id": 47929778,
                            "author": "Benzinga Newsdesk",
                            "content": "",
                            "created_at": "2025-09-29T20:40:00Z",
                            "updated_at": "2025-09-29T20:40:01Z",
                            "headline": "Eric Trump Declares Bitcoin 'The Future' As Shorts Get Liquidated For $83 Million",
                            "source": "benzinga",
                            "summary": "Bitcoin (CRYPTO: BTC) has surged above $114,000...",
                            "symbols": ["ABTC", "BTCUSD"],
                            "url": "https://www.benzinga.com/crypto/cryptocurrency/25/09/47929778/eric-trump-declares-bitcoin-the-future-as-shorts-get-liquidated-for-83-million",
                            "images": [
                                {
                                    "size": "large",
                                    "url": "https://cdn.benzinga.com/files/imagecache/2048x1536xUP/images/story/2025/09/29/Eric-Trump_0.jpeg",
                                }
                            ],
                        }
                    ],
                    "next_page_token": "MTc1OTE3ODQwMTAwMDAwMDAwMHw0NzkyOTc3OA==",
                }
            ]
        },
    }

