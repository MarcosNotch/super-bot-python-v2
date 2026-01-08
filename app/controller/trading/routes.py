"""Routes para el controller de trading."""

from __future__ import annotations

import logging

from fastapi import APIRouter, HTTPException, status

from app.agent.graph.trading_graph import  run_trading_analysis
from app.controller.trading.schemas import TradingAnalysisRequest, TradingAnalysisResponse

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/trading", tags=["trading"])


@router.post(
    "/analyze",
    response_model=TradingAnalysisResponse,
    status_code=status.HTTP_200_OK,
    summary="Ejecutar análisis completo de trading",
    description="""
    Ejecuta el flujo completo de análisis de trading usando el grafo de LangGraph.
    
    El flujo incluye:
    1. Análisis de noticias (sentimiento)
    2. Análisis técnico (SMAs 25/200)
    3. Fear & Greed Index
    4. Soporte y Resistencia
    5. Propuesta del Estratega (Agente 1)
    
    Los pasos 1-4 se ejecutan en paralelo para optimizar tiempo.
    """,
)
async def analyze_trading(request: TradingAnalysisRequest) -> TradingAnalysisResponse:
    """Ejecuta el análisis completo de trading.

    Args:
        request: Parámetros del análisis (símbolos y límite de noticias).

    Returns:
        TradingAnalysisResponse: Resultados completos del análisis.

    Raises:
        HTTPException: Si ocurre un error durante el análisis.
    """
    logger.info(f"Iniciando análisis de trading para {request.symbols}")

    try:
        # Ejecutar el grafo completo
        final_state = await run_trading_analysis(
            symbols=request.symbols,
            news_limit=request.news_limit,
        )

        # Verificar si hubo error
        if final_state.get("error_message"):
            logger.error(f"Error en análisis: {final_state['error_message']}")
            return TradingAnalysisResponse(
                success=False,
                symbols=request.symbols,
                error_message=final_state["error_message"],
            )

        # Construir response con todos los resultados
        response = TradingAnalysisResponse(
            success=True,
            symbols=request.symbols,
            error_message=None,
            news_analysis={
                "sentiment": final_state.get("news_sentiment"),
                "context_summary": final_state.get("news_context_summary"),
                "market_opinion": final_state.get("news_market_opinion"),
            },
            technical_analysis={
                "trend_analysis": final_state.get("technical_analysis_trend"),
                "crossover_status": final_state.get("technical_analysis_crossover"),
                "momentum": final_state.get("technical_analysis_momentum"),
                "conclusion": final_state.get("technical_analysis_conclusion"),
            },
            fear_greed={
                "index": final_state.get("fear_greed_index"),
                "classification": final_state.get("fear_greed_classification"),
            },
            support_resistance={
                "nearest_support": final_state.get("nearest_support"),
                "distance_to_support": final_state.get("distance_to_support"),
                "nearest_resistance": final_state.get("nearest_resistance"),
                "distance_to_resistance": final_state.get("distance_to_resistance"),
            },
            strategist_proposal={
                "direction": final_state.get("strategist_direction"),
                "justification": final_state.get("strategist_justification"),
                "proposal_text": final_state.get("strategist_proposal"),
            },
            skeptic_critique={
                "overall_assessment": final_state.get("skeptic_recommendation"),
                "critique_text": final_state.get("skeptic_critique"),
                "identified_risks": final_state.get("skeptic_risks"),
            },
            executor_decision={
                "final_decision": final_state.get("executor_decision"),
                "reasoning": final_state.get("executor_reasoning"),
                "risk_assessment": final_state.get("executor_final_params", {}).get("risk_assessment"),
                "confidence_level": final_state.get("executor_final_params", {}).get("confidence_level"),
                "has_current_position": final_state.get("executor_final_params", {}).get("has_current_position"),
                "decision_text": final_state.get("executor_decision_text"),
            },
        )

        logger.info(f"Análisis completado exitosamente para {request.symbols}")
        return response

    except Exception as exc:
        logger.error(f"Error ejecutando análisis de trading: {exc}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error ejecutando análisis: {str(exc)}",
        ) from exc


@router.get(
    "/health",
    status_code=status.HTTP_200_OK,
    summary="Health check del servicio de trading",
)
async def health_check() -> dict:
    """Health check endpoint.

    Returns:
        dict: Estado del servicio.
    """
    return {
        "status": "healthy",
        "service": "trading-analysis",
        "version": "1.0.0",
    }


@router.get(
    "/scheduler/status",
    status_code=status.HTTP_200_OK,
    summary="Estado del scheduler de análisis automático",
    description="""
    Consulta el estado del scheduler de análisis automático.
    
    Muestra:
    - Si el scheduler está activo
    - Jobs programados (9:00 AM y 6:00 PM)
    - Próxima ejecución de cada job
    """,
)
async def scheduler_status() -> dict:
    """Consulta el estado del scheduler.

    Returns:
        dict: Estado del scheduler y jobs programados.
    """
    status = get_scheduler_status()

    return {
        "scheduler_active": status["running"],
        "scheduled_jobs": status["jobs"],
        "config": {
            "symbols": ["BTCUSD"],
            "news_limit": 10,
            "schedule": [
                {"time": "09:00", "description": "Análisis matutino"},
                {"time": "18:00", "description": "Análisis vespertino"},
            ],
        },
    }


