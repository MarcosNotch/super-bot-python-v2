"""Modelos de base de datos SQLAlchemy."""

from __future__ import annotations

from datetime import datetime
from typing import Optional

from sqlalchemy import DECIMAL, BigInteger, Index, String, Text, TIMESTAMP
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    """Base class para todos los modelos de SQLAlchemy."""

    pass


class SupportResistanceZone(Base):
    """Modelo para la tabla support_resistance_zones.

    Almacena zonas de soporte y resistencia para análisis técnico.
    """

    __tablename__ = "support_resistance_zones"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    symbol: Mapped[str] = mapped_column(String(20), nullable=False, index=True)
    type: Mapped[str] = mapped_column(String(20), nullable=False, index=True)
    price: Mapped[float] = mapped_column(DECIMAL(18, 2), nullable=False)
    strength: Mapped[str] = mapped_column(String(20), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP, nullable=False, default=lambda: datetime.now(timezone.utc), index=True
    )

    # Índices adicionales definidos en __table_args__
    __table_args__ = (
        Index("idx_symbol", "symbol"),
        Index("idx_type", "type"),
        Index("idx_created_at", "created_at"),
    )

    def __repr__(self) -> str:
        return (
            f"<SupportResistanceZone(id={self.id}, symbol={self.symbol}, "
            f"type={self.type}, price={self.price})>"
        )


class Transaction(Base):
    """Modelo para la tabla transactions.

    Almacena todas las transacciones de compra/venta del bot.
    """

    __tablename__ = "transactions"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    symbol: Mapped[str] = mapped_column(String(20), nullable=False, index=True)
    action: Mapped[str] = mapped_column(String(10), nullable=False)  # "buy" o "sell"
    quantity: Mapped[float] = mapped_column(DECIMAL(18, 8), nullable=False)
    price: Mapped[float] = mapped_column(DECIMAL(18, 2), nullable=False)
    total: Mapped[float] = mapped_column(DECIMAL(18, 2), nullable=False)
    portfolio_value: Mapped[Optional[float]] = mapped_column(DECIMAL(18, 2), nullable=True)
    available_usd: Mapped[Optional[float]] = mapped_column(DECIMAL(18, 2), nullable=True)
    pnl: Mapped[Optional[float]] = mapped_column(DECIMAL(18, 2), nullable=True)
    reason: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[Optional[datetime]] = mapped_column(
        TIMESTAMP, nullable=True, default=lambda: datetime.now(timezone.utc), index=True
    )
    agent_name: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)

    # Índices adicionales
    __table_args__ = (
        Index("idx_symbol", "symbol"),
        Index("idx_created_at", "created_at"),
    )

    def __repr__(self) -> str:
        return (
            f"<Transaction(id={self.id}, symbol={self.symbol}, "
            f"action={self.action}, quantity={self.quantity}, price={self.price})>"
        )

