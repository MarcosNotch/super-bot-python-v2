"""Configuración y gestión de la base de datos MySQL (async).

Reglas:
- Usar AsyncEngine y AsyncSession para operaciones async
- Connection pooling configurado para performance
- Singleton del engine (no recrear en cada request)
"""

from __future__ import annotations

import logging
from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from app.config.settings import settings

logger = logging.getLogger(__name__)

# Motor async singleton (se crea una sola vez)
_async_engine: AsyncEngine | None = None


def get_async_engine() -> AsyncEngine:
    """Devuelve el motor async de SQLAlchemy (singleton).

    Returns:
        AsyncEngine: Motor configurado con connection pooling.
    """
    global _async_engine

    if _async_engine is None:
        # Construir URL de conexión MySQL async
        database_url = (
            f"mysql+aiomysql://{settings.mysql_user}:{settings.mysql_password}"
            f"@{settings.mysql_host}:{settings.mysql_port}/{settings.mysql_database}"
        )

        _async_engine = create_async_engine(
            database_url,
            pool_size=settings.mysql_pool_size,
            max_overflow=settings.mysql_max_overflow,
            pool_timeout=settings.mysql_pool_timeout,
            pool_recycle=settings.mysql_pool_recycle,
            pool_pre_ping=True,  # Verificar conexiones antes de usar
            echo=False,  # Cambiar a True para debug SQL
        )

        logger.info(
            f"Motor de base de datos async creado: {settings.mysql_host}:{settings.mysql_port}/{settings.mysql_database}"
        )

    return _async_engine


# Session factory async
AsyncSessionLocal = sessionmaker(
    bind=get_async_engine(),
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)


async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    """Dependency para obtener una sesión de base de datos async.

    Uso en FastAPI:
        @router.get("/zones")
        async def get_zones(db: AsyncSession = Depends(get_db_session)):
            ...

    Yields:
        AsyncSession: Sesión de base de datos.
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def close_db_connections() -> None:
    """Cierra todas las conexiones del pool.

    Llamar en el shutdown de la aplicación FastAPI.
    """
    global _async_engine

    if _async_engine is not None:
        await _async_engine.dispose()
        logger.info("Conexiones de base de datos cerradas")
        _async_engine = None

