import logging
from datetime import datetime
from typing import Any, Dict, List, Optional

import httpx

from app.config.settings import settings
from app.models.alpaca_news_models import AlpacaNewsResponse

logger = logging.getLogger(__name__)


class AlpacaNewsClientError(Exception):
    """Error de alto nivel al consumir la API de noticias de Alpaca."""

    def __init__(self, message: str, *, status_code: Optional[int] = None) -> None:
        super().__init__(message)
        self.status_code = status_code


class AlpacaNewsClient:
    """Cliente HTTP para consumir la API de noticias de Alpaca.

    Usa un `httpx.AsyncClient` compartido con connection pooling para evitar
    recrear conexiones en cada request.
    """

    def __init__(self) -> None:
        limits = httpx.Limits(
            max_keepalive_connections=settings.alpaca_max_keepalive_connections,
            max_connections=settings.alpaca_max_connections,
            keepalive_expiry=settings.alpaca_keepalive_expiry,
        )

        default_headers = {
            "APCA-API-KEY-ID": settings.alpaca_api_key,
            "APCA-API-SECRET-KEY": settings.alpaca_api_secret,
            "accept": "application/json",
        }

        self._client = httpx.AsyncClient(
            base_url=settings.alpaca_news_base_url,
            timeout=settings.alpaca_news_timeout,
            limits=limits,
            http2=True,
            follow_redirects=True,
            headers=default_headers,
        )

    async def aclose(self) -> None:
        """Cierra el cliente HTTP y libera el pool de conexiones."""

        await self._client.aclose()

    async def get_news(
        self,
        *,
        start: Optional[datetime] = None,
        end: Optional[datetime] = None,
        symbols: Optional[List[str]] = None,
        limit: Optional[int] = None,
        include_content: Optional[bool] = None,
        page_token: Optional[str] = None,
    ) -> AlpacaNewsResponse:
        """Obtiene noticias desde la API de Alpaca.

        Args:
            start: Fecha/hora de inicio del rango (UTC).
            end: Fecha/hora de fin del rango (UTC).
            symbols: Lista de símbolos a filtrar (p.ej. ["BTCUSD"]).
            limit: Límite máximo de resultados.
            include_content: Si se debe incluir el contenido completo de la noticia.
            page_token: Token de paginación para obtener la siguiente página.

        Returns:
            AlpacaNewsResponse: Respuesta tipada con el listado de noticias y token de
            siguiente página si existe.

        Raises:
            AlpacaNewsClientError: Si ocurre un error HTTP o de red al llamar a Alpaca.
        """

        params: Dict[str, Any] = {}

        if start is not None:
            params["start"] = start.isoformat().replace("+00:00", "Z")
        if end is not None:
            params["end"] = end.isoformat().replace("+00:00", "Z")
        if symbols:
            params["symbols"] = ",".join(symbols)
        if limit is not None:
            params["limit"] = limit
        if include_content is not None:
            params["include_content"] = str(include_content).lower()
        if page_token is not None:
            params["page_token"] = page_token

        try:
            response = await self._client.get("/v1beta1/news", params=params)
            response.raise_for_status()
        except httpx.HTTPStatusError as exc:
            status_code = exc.response.status_code
            logger.error(
                "Error HTTP al llamar a Alpaca News: %s - %s",
                status_code,
                exc.response.text,
            )
            raise AlpacaNewsClientError(
                f"Error HTTP al llamar a Alpaca News (status={status_code})",
                status_code=status_code,
            ) from exc
        except httpx.HTTPError as exc:  # errores de red, timeouts, etc.
            logger.error("Error de red al llamar a Alpaca News: %s", str(exc))
            raise AlpacaNewsClientError("Error de red al llamar a Alpaca News") from exc

        data = response.json()
        return AlpacaNewsResponse.model_validate(data)


alpaca_news_client = AlpacaNewsClient()

