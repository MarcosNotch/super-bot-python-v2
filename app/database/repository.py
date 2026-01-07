"""Repositorio para operaciones CRUD sobre support_resistance_zones."""

from __future__ import annotations

import logging
from datetime import datetime
from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.database_models import SupportResistanceZone

logger = logging.getLogger(__name__)


class SupportResistanceRepository:
    """Repositorio para gestionar zonas de soporte y resistencia.

    Centraliza las queries y operaciones de base de datos.
    """

    def __init__(self, session: AsyncSession) -> None:
        """Inicializa el repositorio con una sesión.

        Args:
            session: Sesión async de SQLAlchemy.
        """
        self.session = session

    async def create(
        self,
        *,
        symbol: str,
        type_: str,
        price: float,
        strength: str,
        description: Optional[str] = None,
    ) -> SupportResistanceZone:
        """Crea una nueva zona de soporte/resistencia.

        Args:
            symbol: Símbolo del activo (ej. "BTCUSD").
            type_: Tipo de zona ("support" o "resistance").
            price: Precio de la zona.
            strength: Fortaleza ("weak", "medium", "strong").
            description: Descripción opcional.

        Returns:
            SupportResistanceZone: Zona creada con ID asignado.
        """
        zone = SupportResistanceZone(
            symbol=symbol,
            type=type_,
            price=price,
            strength=strength,
            description=description,
            created_at=datetime.utcnow(),
        )

        self.session.add(zone)
        await self.session.flush()
        await self.session.refresh(zone)

        logger.info(f"Zona creada: {zone}")
        return zone

    async def get_by_id(self, zone_id: int) -> Optional[SupportResistanceZone]:
        """Obtiene una zona por ID.

        Args:
            zone_id: ID de la zona.

        Returns:
            SupportResistanceZone o None si no existe.
        """
        result = await self.session.execute(
            select(SupportResistanceZone).where(SupportResistanceZone.id == zone_id)
        )
        return result.scalar_one_or_none()

    async def get_by_symbol(
        self, symbol: str, limit: int = 100
    ) -> List[SupportResistanceZone]:
        """Obtiene zonas por símbolo, ordenadas por fecha de creación desc.

        Args:
            symbol: Símbolo del activo.
            limit: Número máximo de resultados.

        Returns:
            Lista de zonas.
        """
        result = await self.session.execute(
            select(SupportResistanceZone)
            .where(SupportResistanceZone.symbol == symbol)
            .order_by(SupportResistanceZone.created_at.desc())
            .limit(limit)
        )
        return list(result.scalars().all())

    async def get_by_symbol_and_type(
        self, symbol: str, type_: str, limit: int = 50
    ) -> List[SupportResistanceZone]:
        """Obtiene zonas por símbolo y tipo.

        Args:
            symbol: Símbolo del activo.
            type_: Tipo de zona ("support" o "resistance").
            limit: Número máximo de resultados.

        Returns:
            Lista de zonas.
        """
        result = await self.session.execute(
            select(SupportResistanceZone)
            .where(
                SupportResistanceZone.symbol == symbol,
                SupportResistanceZone.type == type_,
            )
            .order_by(SupportResistanceZone.created_at.desc())
            .limit(limit)
        )
        return list(result.scalars().all())

    async def delete(self, zone_id: int) -> bool:
        """Elimina una zona por ID.

        Args:
            zone_id: ID de la zona a eliminar.

        Returns:
            True si se eliminó, False si no existía.
        """
        zone = await self.get_by_id(zone_id)
        if zone is None:
            return False

        await self.session.delete(zone)
        logger.info(f"Zona eliminada: {zone_id}")
        return True

    async def delete_old_zones(self, symbol: str, days: int = 30) -> int:
        """Elimina zonas antiguas de un símbolo.

        Args:
            symbol: Símbolo del activo.
            days: Días de antigüedad para considerar una zona vieja.

        Returns:
            Número de zonas eliminadas.
        """
        cutoff_date = datetime.now(timezone.utc) - timedelta(days=days)

        result = await self.session.execute(
            select(SupportResistanceZone).where(
                SupportResistanceZone.symbol == symbol,
                SupportResistanceZone.created_at < cutoff_date,
            )
        )
        zones = list(result.scalars().all())

        for zone in zones:
            await self.session.delete(zone)

        count = len(zones)
        logger.info(f"Eliminadas {count} zonas antiguas de {symbol}")
        return count

