"""FastAPI application entry point."""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware

from app.controller.trading import router as trading_router
from app.database import close_db_connections
from app.utils.scheduler import start_scheduler, stop_scheduler

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifecycle manager para la aplicación FastAPI.

    Maneja startup y shutdown de recursos.
    """
    # Startup
    logger.info("🚀 Iniciando aplicación SuperBotV2...")
    logger.info("✅ Grafo de trading cargado")

    # Iniciar scheduler de análisis automático
    start_scheduler()

    yield

    # Shutdown
    logger.info("🔌 Cerrando conexiones...")

    # Detener scheduler
    stop_scheduler()

    await close_db_connections()
    logger.info("✅ Aplicación cerrada correctamente")


# Crear aplicación FastAPI
app = FastAPI(
    title="SuperBotV2 - Crypto Trading API",
    description="""
    API de trading automatizado con análisis de mercado usando LangGraph.
    
    ## Características
    
    * **Análisis de noticias** - Sentimiento del mercado
    * **Análisis técnico** - SMAs y momentum
    * **Fear & Greed Index** - Indicador de sentimiento
    * **Soporte/Resistencia** - Niveles clave para S/L y T/P
    * **Trading Committee** - Sistema de 3 agentes para decisiones
    
    ## Flujo de Análisis
    
    1. Ejecución paralela de análisis (noticias, técnico, F&G, S/R)
    2. Agente Estratega propone trade
    3. (Próximamente) Agente Abogado del Diablo critica
    4. (Próximamente) Agente Juez decide ejecución
    """,
    version="1.0.0",
    lifespan=lifespan,
)

# Middlewares
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En producción, especificar orígenes
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(GZipMiddleware, minimum_size=1000)

# Routers
app.include_router(trading_router)


@app.get("/", tags=["root"])
async def root() -> dict:
    """Root endpoint.

    Returns:
        dict: Información básica de la API.
    """
    return {
        "name": "SuperBotV2 - Crypto Trading API",
        "version": "1.0.0",
        "status": "operational",
        "endpoints": {
            "trading_analysis": "/api/trading/analyze",
            "health": "/api/trading/health",
            "docs": "/docs",
            "redoc": "/redoc",
        },
    }


@app.get("/health", tags=["health"])
async def health() -> dict:
    """Health check general.

    Returns:
        dict: Estado de salud de la aplicación.
    """
    return {
        "status": "healthy",
        "application": "SuperBotV2",
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,  # Solo para desarrollo
        log_level="info",
    )

