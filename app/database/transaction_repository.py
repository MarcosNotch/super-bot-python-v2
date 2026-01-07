"""Repositorio para operaciones de trading (compra/venta) sobre transactions."""

from __future__ import annotations

import logging
from datetime import datetime, timedelta, timezone
from decimal import Decimal
from typing import Dict, List, Optional

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.database_models import Transaction

logger = logging.getLogger(__name__)


class InsufficientFundsError(Exception):
    """Error cuando no hay fondos suficientes para comprar."""

    pass


class InsufficientQuantityError(Exception):
    """Error cuando no hay cantidad suficiente para vender."""

    pass


class TransactionRepository:
    """Repositorio para gestionar transacciones de compra/venta.

    Incluye lógica de negocio para validar y ejecutar trades.
    """

    def __init__(self, session: AsyncSession) -> None:
        """Inicializa el repositorio con una sesión.

        Args:
            session: Sesión async de SQLAlchemy.
        """
        self.session = session

    async def get_available_balance(self) -> float:
        """Obtiene el balance disponible en USD.

        Returns:
            float: Balance disponible (última transacción o 10000 por defecto).
        """
        result = await self.session.execute(
            select(Transaction.available_usd)
            .where(Transaction.available_usd.isnot(None))
            .order_by(Transaction.created_at.desc())
            .limit(1)
        )
        balance = result.scalar_one_or_none()
        return float(balance) if balance else 10000.0  # Default: $10,000

    async def get_position_quantity(self, symbol: str) -> float:
        """Obtiene la cantidad actual de un símbolo en el portfolio.

        Args:
            symbol: Símbolo del activo (ej. "BTCUSD").

        Returns:
            float: Cantidad disponible del símbolo.
        """
        # Sumar todas las compras
        result_buys = await self.session.execute(
            select(func.sum(Transaction.quantity)).where(
                Transaction.symbol == symbol, Transaction.action == "buy"
            )
        )
        total_buys = result_buys.scalar_one_or_none() or Decimal(0)

        # Restar todas las ventas
        result_sells = await self.session.execute(
            select(func.sum(Transaction.quantity)).where(
                Transaction.symbol == symbol, Transaction.action == "sell"
            )
        )
        total_sells = result_sells.scalar_one_or_none() or Decimal(0)

        return float(total_buys - total_sells)

    async def get_average_buy_price(self, symbol: str) -> Optional[float]:
        """Calcula el precio promedio de compra de un símbolo.

        Args:
            symbol: Símbolo del activo.

        Returns:
            float: Precio promedio o None si no hay compras.
        """
        result = await self.session.execute(
            select(
                func.sum(Transaction.quantity * Transaction.price).label("total_cost"),
                func.sum(Transaction.quantity).label("total_quantity"),
            ).where(Transaction.symbol == symbol, Transaction.action == "buy")
        )
        row = result.one_or_none()

        if not row or not row.total_quantity or row.total_quantity == 0:
            return None

        return float(row.total_cost / row.total_quantity)

    async def calculate_portfolio_value(self, current_prices: Dict[str, float]) -> float:
        """Calcula el valor total del portfolio.

        Args:
            current_prices: Diccionario {symbol: current_price}.

        Returns:
            float: Valor total del portfolio en USD.
        """
        available_usd = await self.get_available_balance()
        total_value = available_usd

        # Para cada símbolo en current_prices, calcular el valor de la posición
        for symbol, current_price in current_prices.items():
            quantity = await self.get_position_quantity(symbol)
            if quantity > 0:
                total_value += quantity * current_price

        return total_value

    async def buy(
        self,
        *,
        symbol: str,
        quantity: float,
        price: float,
        reason: Optional[str] = None,
        agent_name: str = "SuperBot",
    ) -> Transaction:
        """Ejecuta una compra validando fondos disponibles.

        Args:
            symbol: Símbolo a comprar.
            quantity: Cantidad a comprar.
            price: Precio de compra.
            reason: Razón de la compra (opcional).
            agent_name: Nombre del agente que ejecuta.

        Returns:
            Transaction: Transacción creada.

        Raises:
            InsufficientFundsError: Si no hay fondos suficientes.
        """
        total_cost = quantity * price
        available_usd = await self.get_available_balance()

        if total_cost > available_usd:
            raise InsufficientFundsError(
                f"Fondos insuficientes: necesitas ${total_cost:,.2f}, "
                f"tienes ${available_usd:,.2f}"
            )

        # Calcular nuevos valores
        new_available_usd = available_usd - total_cost
        portfolio_value = await self.calculate_portfolio_value({symbol: price})
        portfolio_value += total_cost  # Agregar la nueva compra

        # Crear transacción
        transaction = Transaction(
            symbol=symbol,
            action="buy",
            quantity=quantity,
            price=price,
            total=total_cost,
            portfolio_value=portfolio_value,
            available_usd=new_available_usd,
            pnl=None,  # No hay PnL en compras
            reason=reason,
            created_at=datetime.now(timezone.utc),
            agent_name=agent_name,
        )

        self.session.add(transaction)
        await self.session.flush()
        await self.session.refresh(transaction)

        logger.info(
            f"COMPRA ejecutada: {quantity:.8f} {symbol} @ ${price:,.2f} "
            f"(Total: ${total_cost:,.2f})"
        )

        return transaction

    async def sell(
        self,
        *,
        symbol: str,
        quantity: float,
        price: float,
        reason: Optional[str] = None,
        agent_name: str = "SuperBot",
    ) -> Transaction:
        """Ejecuta una venta validando cantidad disponible y calculando PnL.

        Args:
            symbol: Símbolo a vender.
            quantity: Cantidad a vender.
            price: Precio de venta.
            reason: Razón de la venta (opcional).
            agent_name: Nombre del agente que ejecuta.

        Returns:
            Transaction: Transacción creada.

        Raises:
            InsufficientQuantityError: Si no hay cantidad suficiente.
        """
        available_quantity = await self.get_position_quantity(symbol)

        if quantity > available_quantity:
            raise InsufficientQuantityError(
                f"Cantidad insuficiente: intentas vender {quantity:.8f}, "
                f"tienes {available_quantity:.8f} {symbol}"
            )

        # Calcular valores
        total_revenue = quantity * price
        available_usd = await self.get_available_balance()
        new_available_usd = available_usd + total_revenue

        # Calcular PnL
        avg_buy_price = await self.get_average_buy_price(symbol)
        pnl = None
        if avg_buy_price is not None:
            pnl = (price - avg_buy_price) * quantity

        # Portfolio value
        portfolio_value = await self.calculate_portfolio_value({symbol: price})

        # Crear transacción
        transaction = Transaction(
            symbol=symbol,
            action="sell",
            quantity=quantity,
            price=price,
            total=total_revenue,
            portfolio_value=portfolio_value,
            available_usd=new_available_usd,
            pnl=pnl,
            reason=reason,
            created_at=datetime.now(timezone.utc),
            agent_name=agent_name,
        )

        self.session.add(transaction)
        await self.session.flush()
        await self.session.refresh(transaction)

        pnl_str = f"PnL: ${pnl:,.2f}" if pnl else "PnL: N/A"
        logger.info(
            f"VENTA ejecutada: {quantity:.8f} {symbol} @ ${price:,.2f} "
            f"(Total: ${total_revenue:,.2f}, {pnl_str})"
        )

        return transaction

    async def get_all_transactions(
        self, *, limit: int = 100, symbol: Optional[str] = None
    ) -> List[Transaction]:
        """Obtiene las últimas transacciones.

        Args:
            limit: Número máximo de resultados.
            symbol: Filtrar por símbolo (opcional).

        Returns:
            Lista de transacciones.
        """
        query = select(Transaction).order_by(Transaction.created_at.desc()).limit(limit)

        if symbol:
            query = query.where(Transaction.symbol == symbol)

        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def get_transaction_by_id(self, transaction_id: int) -> Optional[Transaction]:
        """Obtiene una transacción por ID.

        Args:
            transaction_id: ID de la transacción.

        Returns:
            Transaction o None si no existe.
        """
        result = await self.session.execute(
            select(Transaction).where(Transaction.id == transaction_id)
        )
        return result.scalar_one_or_none()

    async def get_portfolio_summary(self) -> Dict[str, any]:
        """Obtiene un resumen del portfolio.

        Returns:
            Diccionario con el resumen del portfolio.
        """
        available_usd = await self.get_available_balance()

        # Obtener todos los símbolos con posiciones
        result = await self.session.execute(
            select(Transaction.symbol).distinct().where(Transaction.action == "buy")
        )
        symbols = [row[0] for row in result.all()]

        positions = {}
        for symbol in symbols:
            quantity = await self.get_position_quantity(symbol)
            if quantity > 0:
                avg_price = await self.get_average_buy_price(symbol)
                positions[symbol] = {"quantity": quantity, "avg_buy_price": avg_price}

        return {
            "available_usd": available_usd,
            "positions": positions,
            "total_positions": len(positions),
        }

    async def get_pnl_summary(self, days: int = 30) -> Dict[str, any]:
        """Calcula el PnL total en un período.

        Args:
            days: Número de días para calcular PnL.

        Returns:
            Diccionario con estadísticas de PnL.
        """
        cutoff_date = datetime.now(timezone.utc) - timedelta(days=days)

        # Sumar PnL de ventas en el período
        result = await self.session.execute(
            select(
                func.sum(Transaction.pnl).label("total_pnl"),
                func.count(Transaction.id).label("num_trades"),
            ).where(
                Transaction.action == "sell",
                Transaction.created_at >= cutoff_date,
                Transaction.pnl.isnot(None),
            )
        )
        row = result.one_or_none()

        total_pnl = float(row.total_pnl) if row and row.total_pnl else 0.0
        num_trades = int(row.num_trades) if row and row.num_trades else 0

        return {
            "period_days": days,
            "total_pnl": total_pnl,
            "num_trades": num_trades,
            "avg_pnl_per_trade": total_pnl / num_trades if num_trades > 0 else 0.0,
        }

