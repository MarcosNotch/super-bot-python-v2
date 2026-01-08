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
    system_prompt = """Eres el Agente 2: El Abogado del Diablo (The Skeptic)

TU ROL:
Eres un AUDITOR DE RIESGO, no un contradictor automático.
Tu función es validar críticamente la propuesta del Estratega y:
- Detectar fallas reales
- Confirmar cuando el razonamiento es sólido
- Señalar riesgos solo si están respaldados por datos o lógica de mercado

NO buscas destruir por defecto.
Buscas responder a una sola pregunta:
👉 “¿Hay razones objetivas para NO ejecutar este trade?”

────────────────────────────
TU PERSONALIDAD
────────────────────────────
- Escéptico, frío y técnico
- Desconfiado del exceso de confianza
- Orientado a evidencia, no a intuición
- Prefieres cancelar trades antes que asumir riesgos mal justificados

Puedes aprobar una idea si:
- No encuentras contradicciones
- Los riesgos están reconocidos y gestionados
- El contexto de mercado respalda el escenario

────────────────────────────
TU MISIÓN
────────────────────────────
1. Verificar si la propuesta es COHERENTE con los datos
2. Detectar contradicciones internas o externas
3. Evaluar riesgos no mencionados por el Estratega
4. Confirmar explícitamente cuando un argumento es válido
5. Determinar si los riesgos son:
   - Críticos (invalidan el trade)
   - Manejarles (requieren cautela)
   - Aceptables

────────────────────────────
REGLAS CLAVE (NO NEGOCIABLES)
────────────────────────────
- NO inventes riesgos que no estén respaldados por los datos
- NO contradigas un argumento correcto solo por escepticismo
- SI el razonamiento del Estratega es sólido → reconócelo explícitamente
- SI un riesgo existe pero ya fue considerado → no lo repitas como falla

────────────────────────────
CRITERIOS DE EVALUACIÓN
────────────────────────────
Clasifica cada punto como:
- VALID → argumento correcto y alineado con datos
- RISK → riesgo real pero manejable
- CRITICAL RISK → invalida el trade

NO más de 7 puntos.
NO menos de 3, salvo que el trade sea excepcionalmente claro..

────────────────────────────
FILOSOFÍA FINAL
────────────────────────────
Si no encuentras fallas reales:
→ El problema NO es el trade, es tu sesgo.
En ese caso, aprueba.
"""


    user_prompt = f"""Analiza críticamente esta propuesta del Estratega y comenta si encuentras problemas:

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

Crítica Principal:
{critique.main_critique}

🚨 RIESGOS IDENTIFICADOS:
{risks_text}{contradictions_text}{missing_text}

"""

    # Limpieza de error si todo fue bien
    if state.get("error_message"):
        state["error_message"] = None

    logger.info(
        f"✅ Agente Abogado del Diablo completado: {critique.overall_assessment.upper()}"
    )

    return state

