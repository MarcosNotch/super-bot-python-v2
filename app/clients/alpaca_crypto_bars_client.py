import logging
from datetime import datetime
from typing import Any, Dict, List, Optional

import httpx

from app.config.settings import settings

from app.models.alpaca_crypto_bars_models import AlpacaCryptoBarsResponse

logger = logging.getLogger(__name__)


class AlpacaCryptoBarsClientError(Exception):
    """Error de alto nivel al consumir la API de crypto bars de Alpaca."""

    def __init__(self, message: str, *, status_code: Optional[int] = None) -> None:
        super().__init__(message)
        self.status_code = status_code


class AlpacaCryptoBarsClient:
    """Cliente HTTP para consumir la API de barras de cripto de Alpaca.

    Usa un `httpx.AsyncClient` compartido con connection pooling.
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
            timeout=settings.alpaca_crypto_bars_timeout,
            limits=limits,
            http2=True,
            follow_redirects=True,
            headers=default_headers,
        )

    async def aclose(self) -> None:
        """Cierra el cliente HTTP y libera el pool de conexiones."""

        await self._client.aclose()

    async def get_crypto_bars(
        self,
        *,
        symbols: List[str],
        timeframe: str,
        start: datetime,
        end: datetime,
        limit: Optional[int] = None,
        sort: Optional[str] = None,
    ) -> AlpacaCryptoBarsResponse:
        """Obtiene barras de cripto desde la API de Alpaca.

        Args:
            symbols: Lista de símbolos en formato "BASE/QUOTE" (ej. ["BTC/USD"]).
            timeframe: Timeframe de los bars (ej. "1D", "1H").
            start: Fecha/hora de inicio del rango (UTC).
            end: Fecha/hora de fin del rango (UTC).
            limit: Límite máximo de resultados.
            sort: Orden de los resultados ("asc" o "desc").

        Returns:
            AlpacaCryptoBarsResponse: Respuesta tipada con las barras por símbolo.

        Raises:
            AlpacaCryptoBarsClientError: Si ocurre un error HTTP o de red.
        """

        params: Dict[str, Any] = {
            "symbols": ",".join(symbols),
            "timeframe": timeframe,
            "start": start.isoformat().replace("+00:00", "Z"),
            "end": end.isoformat().replace("+00:00", "Z"),
        }

        if limit is not None:
            params["limit"] = limit
        if sort is not None:
            params["sort"] = sort

        try:
            response = await self._client.get("/v1beta3/crypto/us/bars", params=params)
            response.raise_for_status()
        except httpx.HTTPStatusError as exc:
            status_code = exc.response.status_code
            logger.error(
                "Error HTTP al llamar a Alpaca Crypto Bars: %s - %s",
                status_code,
                exc.response.text,
            )
            raise AlpacaCryptoBarsClientError(
                f"Error HTTP al llamar a Alpaca Crypto Bars (status={status_code})",
                status_code=status_code,
            ) from exc
        except httpx.HTTPError as exc:
            logger.error("Error de red al llamar a Alpaca Crypto Bars: %s", str(exc))
            raise AlpacaCryptoBarsClientError(
                "Error de red al llamar a Alpaca Crypto Bars"
            ) from exc

        data = response.json()
        return AlpacaCryptoBarsResponse.model_validate(data)


alpaca_crypto_bars_client = AlpacaCryptoBarsClient()

