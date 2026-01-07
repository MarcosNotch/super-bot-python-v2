"""Nodo: busca zonas de soporte/resistencia y calcula distancias al precio actual."""

from __future__ import annotations

import logging
from datetime import datetime, timedelta, timezone
from typing import Optional

from app.agent.state.agent_state import AgentState
from app.clients.alpaca_crypto_bars_client import (
    AlpacaCryptoBarsClientError,
    alpaca_crypto_bars_client,
)
from app.database import AsyncSessionLocal, SupportResistanceRepository

logger = logging.getLogger(__name__)


def _calculate_distance_percentage(current_price: float, target_price: float) -> str:
    """Calcula el porcentaje de distancia entre el precio actual y un objetivo.

    Args:
        current_price: Precio actual del activo.
        target_price: Precio objetivo (soporte o resistencia).

    Returns:
        str: Porcentaje formateado (ej: "-1.5%" o "+2.3%").
    """
    if current_price == 0:
        return "0.0%"

    distance = ((target_price - current_price) / current_price) * 100
    sign = "+" if distance > 0 else ""
    return f"{sign}{distance:.2f}%"


async def _get_current_price(symbol: str) -> Optional[float]:
    """Obtiene el precio actual (close del último bar) de un símbolo.

    Args:
        symbol: Símbolo del activo (formato "BTC/USD").

    Returns:
        float: Precio actual o None si falla.
    """
    try:
        # Obtener el último bar (1 día, último valor)
        end_time = datetime.now(timezone.utc)
        start_time = end_time - timedelta(days=2)  # Últimos 2 días para asegurar datos

        response = await alpaca_crypto_bars_client.get_crypto_bars(
            symbols=[symbol],
            timeframe="1D",
            start=start_time,
            end=end_time,
            limit=1,
            sort="desc",
        )

        # Extraer el último precio close
        if symbol in response.bars and response.bars[symbol]:
            latest_bar = response.bars[symbol][0]
            return float(latest_bar.c)  # Close price

        return None

    except AlpacaCryptoBarsClientError as exc:
        logger.error(f"Error obteniendo precio actual de {symbol}: {exc}")
        return None


async def support_resistance_node(state: AgentState) -> AgentState:
    """Busca las zonas de soporte/resistencia más cercanas y calcula distancias.

    Contract:
    - Input: estado con `symbols` (usa el primero).
    - Output: mismo estado, agregando:
        - `nearest_support` (float): precio del soporte más cercano
        - `distance_to_support` (str): distancia porcentual (ej: "-1.5%")
        - `nearest_resistance` (float): precio de la resistencia más cercana
        - `distance_to_resistance` (str): distancia porcentual (ej: "+1.5%")
      o `error_message` si algo falla.

    Regla LangGraph: siempre devolver el mismo objeto/Tipo de estado.
    """

    # Obtener símbolo
    symbols = state.get("symbols") or ["BTCUSD"]
    symbol = symbols[0] if symbols else "BTCUSD"

    # Formato para Alpaca: BTC/USD
    symbol_alpaca = symbol.replace("USD", "/USD") if "/" not in symbol else symbol

    logger.info(f"Buscando zonas de soporte/resistencia para {symbol}")

    # 1. Obtener precio actual
    current_price = await _get_current_price(symbol_alpaca)

    if current_price is None:
        state["error_message"] = f"No se pudo obtener el precio actual de {symbol}"
        return state

    # Asignar precio actual al estado para que otros nodos lo reutilicen
    state["current_price"] = current_price
    logger.info(f"Precio actual de {symbol}: ${current_price:,.2f}")

    # 2. Consultar zonas desde la base de datos
    async with AsyncSessionLocal() as session:
        repo = SupportResistanceRepository(session)

        # Obtener soportes y resistencias (últimas 50 de cada tipo)
        supports = await repo.get_by_symbol_and_type(symbol, "SOPORTE", limit=50)
        resistances = await repo.get_by_symbol_and_type(symbol, "RESISTENCIA", limit=50)

    if not supports and not resistances:
        state["error_message"] = f"No se encontraron zonas para {symbol} en la base de datos"
        return state

    # 3. Encontrar el soporte más cercano (por debajo del precio actual)
    nearest_support = None
    nearest_support_distance = float("inf")

    for support in supports:
        price = float(support.price)
        if price < current_price:  # Debe estar por debajo
            distance = current_price - price
            if distance < nearest_support_distance:
                nearest_support = price
                nearest_support_distance = distance

    # 4. Encontrar la resistencia más cercana (por encima del precio actual)
    nearest_resistance = None
    nearest_resistance_distance = float("inf")

    for resistance in resistances:
        price = float(resistance.price)
        if price > current_price:  # Debe estar por encima
            distance = price - current_price
            if distance < nearest_resistance_distance:
                nearest_resistance = price
                nearest_resistance_distance = distance

    # 5. Calcular porcentajes
    if nearest_support is not None:
        state["nearest_support"] = nearest_support
        state["distance_to_support"] = _calculate_distance_percentage(
            current_price, nearest_support
        )
        logger.info(
            f"Soporte más cercano: ${nearest_support:,.2f} ({state['distance_to_support']})"
        )
    else:
        logger.warning("No se encontró soporte por debajo del precio actual")

    if nearest_resistance is not None:
        state["nearest_resistance"] = nearest_resistance
        state["distance_to_resistance"] = _calculate_distance_percentage(
            current_price, nearest_resistance
        )
        logger.info(
            f"Resistencia más cercana: ${nearest_resistance:,.2f} ({state['distance_to_resistance']})"
        )
    else:
        logger.warning("No se encontró resistencia por encima del precio actual")

    # Validar que encontramos al menos uno
    if nearest_support is None and nearest_resistance is None:
        state["error_message"] = (
            f"No se encontraron zonas válidas para {symbol} "
            f"(precio actual: ${current_price:,.2f})"
        )
        return state

    # Limpieza de error si todo fue bien
    if state.get("error_message"):
        state["error_message"] = None

    return state

