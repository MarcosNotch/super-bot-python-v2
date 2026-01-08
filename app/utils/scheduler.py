"""Scheduler para ejecución automática del análisis de trading.

Este módulo configura la ejecución programada del grafo de trading
dos veces al día: 9:00 AM y 6:00 PM.
"""

import logging
from typing import List

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

from app.agent.graph.trading_graph import run_trading_analysis

logger = logging.getLogger(__name__)

# Singleton del scheduler
_scheduler: AsyncIOScheduler | None = None


async def _execute_scheduled_analysis(symbols: List[str], news_limit: int) -> None:
    """Ejecuta el análisis de trading programado.

    Args:
        symbols: Lista de símbolos a analizar.
        news_limit: Límite de noticias a analizar.
    """
    logger.info(f"🤖 Ejecutando análisis programado para {symbols}")

    try:
        final_state = await run_trading_analysis(
            symbols=symbols,
            news_limit=news_limit,
        )

        # Log del resultado
        if final_state.get("error_message"):
            logger.error(
                f"❌ Análisis programado falló: {final_state['error_message']}"
            )
        else:
            # Log de la decisión del ejecutor
            executor_decision = final_state.get("executor_decision", "N/A")
            executor_reasoning = final_state.get("executor_reasoning", "N/A")

            logger.info(
                f"✅ Análisis programado completado - Decisión: {executor_decision.upper()}"
            )
            logger.info(f"📊 Razonamiento: {executor_reasoning[:200]}...")

    except Exception as exc:
        logger.error(
            f"❌ Error ejecutando análisis programado: {exc}",
            exc_info=True,
        )


def start_scheduler() -> None:
    """Inicia el scheduler de análisis automático.

    Configura dos ejecuciones diarias:
    - 9:00 AM
    - 6:00 PM

    Los datos de entrada son:
    - symbols: ["BTCUSD"]
    - news_limit: 10
    """
    global _scheduler

    if _scheduler is not None:
        logger.warning("⚠️ Scheduler ya está iniciado")
        return

    # Crear scheduler
    _scheduler = AsyncIOScheduler(timezone="America/Argentina/Buenos_Aires")

    # Parámetros de análisis
    symbols = ["BTCUSD"]
    news_limit = 10

    # Job 1: Análisis a las 9:00 AM
    _scheduler.add_job(
        _execute_scheduled_analysis,
        trigger=CronTrigger(hour=9, minute=0),
        args=[symbols, news_limit],
        id="trading_analysis_morning",
        name="Análisis de Trading - Mañana",
        replace_existing=True,
    )

    # Job 2: Análisis a las 6:00 PM
    _scheduler.add_job(
        _execute_scheduled_analysis,
        trigger=CronTrigger(hour=18, minute=0),
        args=[symbols, news_limit],
        id="trading_analysis_evening",
        name="Análisis de Trading - Tarde",
        replace_existing=True,
    )

    # Iniciar scheduler
    _scheduler.start()

    logger.info("✅ Scheduler iniciado - Ejecuciones programadas:")
    logger.info("   📅 9:00 AM - Análisis matutino")
    logger.info("   📅 6:00 PM - Análisis vespertino")


def stop_scheduler() -> None:
    """Detiene el scheduler de análisis automático."""
    global _scheduler

    if _scheduler is None:
        logger.warning("⚠️ Scheduler no está iniciado")
        return

    _scheduler.shutdown(wait=True)
    _scheduler = None

    logger.info("🛑 Scheduler detenido correctamente")


def get_scheduler_status() -> dict:
    """Obtiene el estado actual del scheduler.

    Returns:
        dict: Información sobre el scheduler y sus jobs.
    """
    if _scheduler is None:
        return {
            "running": False,
            "jobs": [],
        }

    jobs = []
    for job in _scheduler.get_jobs():
        next_run = job.next_run_time.isoformat() if job.next_run_time else None
        jobs.append({
            "id": job.id,
            "name": job.name,
            "next_run": next_run,
        })

    return {
        "running": _scheduler.running,
        "jobs": jobs,
    }

