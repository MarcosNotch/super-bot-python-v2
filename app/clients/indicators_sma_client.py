import logging
from typing import Any, Dict, Optional

import httpx

from app.config.settings import settings
from app.models.indicators_sma_models import IndicatorResponse

logger = logging.getLogger(__name__)


class IndicatorClientError(Exception):
    """Error de alto nivel al consumir la API de indicadores técnicos."""

    def __init__(self, message: str, *, status_code: Optional[int] = None) -> None:
        super().__init__(message)
        self.status_code = status_code


class SimpleMovingAverageClient:
    """Cliente HTTP para consultar medias móviles simples (SMA).

    Implementa un `httpx.AsyncClient` reutilizable con pooling.
    """

    def __init__(self) -> None:
        limits = httpx.Limits(
            max_keepalive_connections=settings.alpaca_max_keepalive_connections,
            max_connections=settings.alpaca_max_connections,
            keepalive_expiry=settings.alpaca_keepalive_expiry,
        )

        default_params = {
            "apiKey": settings.indicators_api_key,
        }

        self._client = httpx.AsyncClient(
            base_url=settings.indicators_base_url,
            timeout=settings.indicators_timeout,
            limits=limits,
            http2=True,
            follow_redirects=True,
            params=default_params,
        )

    async def aclose(self) -> None:
        """Cierra el cliente HTTP y libera el pool de conexiones."""

        await self._client.aclose()

    async def get_sma(
        self,
        *,
        symbol: str,
        timespan: str,
        window: int,
        series_type: str,
        order: Optional[str] = None,
        limit: Optional[int] = None,
        cursor: Optional[str] = None,
    ) -> IndicatorResponse:
        """Obtiene una media móvil simple (SMA) para un símbolo dado.

        Args:
            symbol: Símbolo del activo (ej. "X:BTCUSD").
            timespan: Unidad de tiempo (ej. "day").
            window: Tamaño de la ventana de la SMA (ej. 200).
            series_type: Tipo de serie sobre la que se calcula (ej. "close").
            order: Orden de los resultados ("asc" o "desc").
            limit: Límite máximo de puntos devueltos.
            cursor: Cursor para paginación si se requiere.

        Returns:
            IndicatorResponse: Respuesta tipada con los valores del indicador.

        Raises:
            IndicatorClientError: Si ocurre un error HTTP o de red.
        """

        params: Dict[str, Any] = {
            "timespan": timespan,
            "window": window,
            "series_type": series_type,
        }

        if order is not None:
            params["order"] = order
        if limit is not None:
            params["limit"] = limit
        if cursor is not None:
            params["cursor"] = cursor

        endpoint = f"/v1/indicators/sma/{symbol}"

        try:
            response = await self._client.get(endpoint, params=params)
            response.raise_for_status()
        except httpx.HTTPStatusError as exc:
            status_code = exc.response.status_code
            logger.error(
                "Error HTTP al llamar a SMA: %s - %s",
                status_code,
                exc.response.text,
            )
            raise IndicatorClientError(
                f"Error HTTP al llamar a SMA (status={status_code})",
                status_code=status_code,
            ) from exc
        except httpx.HTTPError as exc:
            logger.error("Error de red al llamar a SMA: %s", str(exc))
            raise IndicatorClientError("Error de red al llamar a SMA") from exc

        data = response.json()
        return IndicatorResponse.model_validate(data)


sma_client = SimpleMovingAverageClient()

