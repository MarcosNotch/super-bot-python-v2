"""Nodo: Agente 2 - El Abogado del Diablo (The Skeptic).

Este agente es pesimista y desconfiado por diseño.
Su misión es destruir la propuesta del Estratega encontrando inconsistencias y riesgos.
"""

from __future__ import annotations

import logging
from typing import Dict
from app.agent.state.agent_state import AgentState
from app.models.skeptic_models import SkepticCritique
from app.utils.agent_executor import AgentExecutorError, agent_executor
from app.database import AsyncSessionLocal, TransactionRepository
logger = logging.getLogger(__name__)

async def _get_current_position_context(symbol: str) -> Dict[str, any]:
    """Obtiene el contexto de la posición actual del portfolio.

    Args:
        symbol: Símbolo del activo.

    Returns:
        Diccionario con información de posición y balance.
    """
    async with AsyncSessionLocal() as session:
        repo = TransactionRepository(session)

        # Obtener posición actual
        quantity = await repo.get_position_quantity(symbol)

        # Obtener balance disponible
        available_usd = await repo.get_available_balance()

        # Obtener precio promedio si hay posición
        avg_buy_price = None
        if quantity > 0:
            avg_buy_price = await repo.get_average_buy_price(symbol)

        return {
            "has_position": quantity > 0,
            "current_quantity": quantity,
            "average_buy_price": avg_buy_price,
            "available_usd": available_usd,
            "can_buy": available_usd > 0,
            "can_sell": quantity > 0,
        }

def _build_position_context_text(position: Dict[str, any], symbol: str) -> str:
    """Construye texto legible sobre la posición actual.

    Args:
        position: Diccionario con datos de posición.
        symbol: Símbolo del activo.

    Returns:
        str: Texto formateado.
    """
    if position["has_position"]:
        return f"""
=== POSICIÓN ACTUAL EN {symbol} ===

✅ TIENES POSICIÓN ABIERTA
  • Cantidad: {position['current_quantity']:.8f}
  • Precio promedio de compra: ${position['average_buy_price']:,.2f}
  • Valor estimado: ${position['current_quantity'] * position['average_buy_price']:,.2f}

💵 Balance disponible: ${position['available_usd']:,.2f} USD

ACCIONES DISPONIBLES:
  • SELL - Puedes cerrar la posición
  • HOLD - Mantener la posición actual
"""
    else:
        return f"""
=== POSICIÓN ACTUAL EN {symbol} ===

⚪ NO TIENES POSICIÓN ABIERTA
  • Cantidad: 0
  • Sin exposición al activo

💵 Balance disponible: ${position['available_usd']:,.2f} USD

ACCIONES DISPONIBLES:
  • BUY - Puedes abrir posición si el análisis es favorable
  • HOLD - Esperar mejor oportunidad
"""

def _build_strategist_proposal_context(state: AgentState) -> str:
    """Construye el contexto de la propuesta del Estratega.

    Args:
        state: Estado con la propuesta del Estratega.

    Returns:
        str: Texto formateado con la propuesta completa.
    """
    proposal_text = state.get("strategist_proposal", "N/A")

    return f"""
{proposal_text}
"""


async def _build_market_context_for_skeptic(state: AgentState) -> str:
    """Construye el contexto de mercado para el Abogado del Diablo.

    Args:
        state: Estado con todos los análisis.

    Returns:
        str: Texto formateado con el contexto de mercado.
    """
    position = await _get_current_position_context("BTCUSD")
    position_text = _build_position_context_text(position, "BTCUSD")

    lines = [
        "=== CONTEXTO DE MERCADO (Para Verificación) ===",
        "",
        "📰 NOTICIAS:",
        f"  • Sentimiento: {state.get('news_sentiment', 'N/A')}",
        f"  • Contexto: {state.get('news_context_summary', 'N/A')[:100]}...",
        f"  • Opinión: {state.get('news_market_opinion', 'N/A')[:100]}...",
        "",
        "📈 ANÁLISIS TÉCNICO:",
        f"  • Momentum: {state.get('technical_analysis_momentum', 'N/A')}",
        f"  • Cruce SMA: {state.get('technical_analysis_crossover', 'N/A')}",
        f"  • Conclusión: {state.get('technical_analysis_conclusion', 'N/A')[:100]}...",
        "",
        "😨 FEAR & GREED:",
        f"  • Índice: {state.get('fear_greed_index', 'N/A')}/100",
        f"  • Clasificación: {state.get('fear_greed_classification', 'N/A')}",
        "",
        "🎯 SOPORTE/RESISTENCIA:",
        f"  • Soporte: ${state.get('nearest_support', 0):,.2f} ({state.get('distance_to_support', 'N/A')})",
        f"  • Resistencia: ${state.get('nearest_resistance', 0):,.2f} ({state.get('distance_to_resistance', 'N/A')})",
        position_text
    ]

    return "\n".join(lines)


async def skeptic_agent_node(state: AgentState) -> AgentState:
    """Agente 2: El Abogado del Diablo (The Skeptic).

    Analiza críticamente la propuesta del Estratega, busca inconsistencias,
    identifica riesgos y proporciona una evaluación pesimista pero fundamentada.

    Es desconfiado por diseño y su trabajo es encontrar problemas.

    Contract:
    - Input: estado con la propuesta del Estratega + datos de mercado.
    - Output: mismo estado, agregando:
        - `skeptic_critique` (str): crítica completa
        - `skeptic_risks` (List[str]): lista de riesgos identificados
        - `skeptic_recommendation` (str): "reject" | "proceed_with_caution" | "acceptable"
      o `error_message` si algo falla.

    Regla LangGraph: siempre devolver el mismo objeto/Tipo de estado.
    """

    logger.info("😈 Agente 2 (El Abogado del Diablo) iniciando crítica...")

    # Verificar que tenemos la propuesta del Estratega
    if not state.get("strategist_direction"):
        state["error_message"] = "No hay propuesta del Estratega para criticar"
        return state

    # 1. Construir contextos
    strategist_context = _build_strategist_proposal_context(state)
    market_context = await _build_market_context_for_skeptic(state)

    # 2. Crear prompt para el LLM
    system_prompt = """Eres "El Abogado del Diablo" (The Skeptic), el Agente 2 del Trading Committee.

TU PERSONALIDAD:
- Eres PESIMISTA y DESCONFIADO por diseño
- Tu único trabajo es DESTRUIR la propuesta del Agente 1 (El Estratega)
- Buscas INCONSISTENCIAS, CONTRADICCIONES y RIESGOS ignorados
- Eres MORDAZ y directo en tu crítica

TU TRABAJO:
1. Analizar críticamente la propuesta del Estratega
2. Comparar su propuesta con los datos reales del mercado
3. Considerar la POSICIÓN ACTUAL del portfolio
4. Identificar TODO lo que puede salir mal
5. Buscar específicamente:
   - Contradicciones en su lógica
   - Riesgos que minimizó o ignoró
   - Sesgos de confirmación
   - Factores que no consideró
   - Señales de peligro que omitió

REGLAS ESPECÍFICAS:
- Si Fear & Greed > 75 y el Estratega quiere COMPRAR → Señala trampa de liquidez
- Si precio en zona ALTA del rango y propone COMPRAR → Critica riesgo de reversión
- Si noticias son "demasiado positivas" → Sospecha que ya están descontadas
- Si el Estratega usa palabras como "sólido", "confirmado", "fuerte" → Cuestiona el exceso de confianza
- Si hay CUALQUIER contradicción → Atácala sin piedad
- Si YA TIENES posición y propone BUY → Critica SOBREEXPOSICIÓN al riesgo
- Si NO TIENES posición y propone SELL → Señala que es IMPOSIBLE vender sin posición

TU OBJETIVO:
- Overall assessment: "reject" si encuentras riesgos críticos
- Overall assessment: "proceed_with_caution" si hay riesgos manejables
- Overall assessment: "acceptable" solo si realmente no encuentras problemas graves (raro)

IMPORTANTE:
- NO seas neutral ni equilibrado - eres el CRÍTICO
- Identifica entre 3-7 riesgos específicos
- Sé MORDAZ pero fundamentado en datos
- Si el Estratega está equivocado, demuéstralo con los mismos datos que él usó
- CONSIDERA SIEMPRE la posición actual en tu crítica

Devuelve SOLO un JSON con el formato especificado."""

    user_prompt = f"""Analiza críticamente esta propuesta del Estratega y DESTRUYELA si encuentras problemas:

{strategist_context}

{market_context}

Recuerda: Eres el ABOGADO DEL DIABLO. Tu trabajo es encontrar TODO lo que puede salir mal.

Devuelve SOLO JSON válido."""

    # 3. Ejecutar con AgentExecutor
    try:
        critique = await agent_executor.execute(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            response_model=SkepticCritique,
            context={
                "agent": "skeptic",
                "strategist_direction": state.get("strategist_direction"),
            },
        )
    except AgentExecutorError as exc:
        logger.error(f"Error ejecutando Agente Abogado del Diablo: {exc}", exc_info=True)
        state["error_message"] = f"Error en Agente Abogado del Diablo: {str(exc)}"
        return state

    # 4. Asignar resultados al estado
    state["skeptic_recommendation"] = critique.overall_assessment
    state["skeptic_risks"] = critique.identified_risks

    # Construir crítica completa en texto
    risks_text = "\n".join([f"  ⚠️  {risk}" for risk in critique.identified_risks])

    contradictions_text = ""
    if critique.contradictions:
        contradictions_text = "\n\n🔍 CONTRADICCIONES ENCONTRADAS:\n" + "\n".join(
            [f"  • {c}" for c in critique.contradictions]
        )

    missing_text = ""
    if critique.missing_considerations:
        missing_text = "\n\n❌ FACTORES IGNORADOS:\n" + "\n".join(
            [f"  • {m}" for m in critique.missing_considerations]
        )

    state["skeptic_critique"] = f"""
😈 CRÍTICA DEL ABOGADO DEL DIABLO

Evaluación: {critique.overall_assessment.upper().replace('_', ' ')}

Crítica Principal:
{critique.main_critique}

🚨 RIESGOS IDENTIFICADOS:
{risks_text}{contradictions_text}{missing_text}

💡 Recomendación:
{critique.recommendation}
"""

    # Limpieza de error si todo fue bien
    if state.get("error_message"):
        state["error_message"] = None

    logger.info(
        f"✅ Agente Abogado del Diablo completado: {critique.overall_assessment.upper()}"
    )

    return state

