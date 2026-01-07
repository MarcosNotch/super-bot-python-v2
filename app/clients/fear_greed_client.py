import logging
from typing import Any, Dict

import httpx

from app.config.settings import settings
from app.models.fear_greed_models import FearGreedResponse

logger = logging.getLogger(__name__)


class FearGreedClientError(Exception):
    """Error de alto nivel al consumir la API del índice Fear & Greed."""

    def __init__(self, message: str) -> None:
        super().__init__(message)


class FearGreedClient:
    """Cliente HTTP para consultar el índice Fear & Greed de alternative.me.

    Usa un `httpx.AsyncClient` compartido con connection pooling.
    """

    def __init__(self) -> None:
        limits = httpx.Limits(
            max_keepalive_connections=settings.alpaca_max_keepalive_connections,
            max_connections=settings.alpaca_max_connections,
            keepalive_expiry=settings.alpaca_keepalive_expiry,
        )

        self._client = httpx.AsyncClient(
            base_url=settings.fear_greed_base_url,
            timeout=settings.fear_greed_timeout,
            limits=limits,
            http2=True,
            follow_redirects=True,
        )

    async def aclose(self) -> None:
        """Cierra el cliente HTTP y libera el pool de conexiones."""

        await self._client.aclose()

    async def get_latest(self, *, limit: int = 1) -> FearGreedResponse:
        """Obtiene los últimos valores del índice Fear & Greed.

        Args:
            limit: Número máximo de registros a recuperar (por defecto 1).

        Returns:
            FearGreedResponse: Respuesta tipada con los valores del índice.

        Raises:
            FearGreedClientError: Si ocurre un error HTTP o de red.
        """

        params: Dict[str, Any] = {"limit": limit}

        try:
            response = await self._client.get("/fng/", params=params)
            response.raise_for_status()
        except httpx.HTTPStatusError as exc:
            logger.error(
                "Error HTTP al llamar a Fear & Greed Index: %s - %s",
                exc.response.status_code,
                exc.response.text,
            )
            raise FearGreedClientError(
                f"Error HTTP al llamar a Fear & Greed Index (status={exc.response.status_code})"
            ) from exc
        except httpx.HTTPError as exc:
            logger.error("Error de red al llamar a Fear & Greed Index: %s", str(exc))
            raise FearGreedClientError("Error de red al llamar a Fear & Greed Index") from exc

        data = response.json()
        return FearGreedResponse.model_validate(data)


fear_greed_client = FearGreedClient()

