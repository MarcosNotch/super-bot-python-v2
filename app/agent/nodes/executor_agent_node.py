"""Nodo: Agente 3 - El Juez de Riesgo (The Executor).

Este agente es frío y equilibrado por diseño.
Su misión es evaluar objetivamente los argumentos del Estratega y el Abogado del Diablo,
y tomar la decisión final considerando la posición actual del portfolio.
"""

from __future__ import annotations

import logging
from typing import Dict

from app.agent.state.agent_state import AgentState
from app.database import AsyncSessionLocal, TransactionRepository
from app.models.executor_models import ExecutorDecision
from app.utils.agent_executor import AgentExecutorError, agent_executor

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
  • HOLD - Mantener la posición actual
"""


def _build_debate_summary(state: AgentState) -> str:
    """Construye el resumen del debate entre Estratega y Abogado del Diablo.

    Args:
        state: Estado con las propuestas de ambos agentes.

    Returns:
        str: Texto formateado con el debate.
    """
    # Propuesta del Estratega
    strategist_direction = state.get("strategist_direction", "N/A")
    strategist_justification = state.get("strategist_justification", "N/A")

    # Crítica del Abogado del Diablo
    skeptic_risks = state.get("skeptic_risks", [])
    skeptic_critique = state.get("skeptic_critique", "N/A")

    risks_text = "\n".join([f"    • {risk}" for risk in skeptic_risks])

    return f"""
=== DEBATE: ESTRATEGA vs ABOGADO DEL DIABLO ===

🎯 Agente ESTRATEGA:
  Propuesta: {strategist_direction.upper()}
  
  Justificación:
  {strategist_justification}

😈 Agente Esceptico:
  {skeptic_critique}...
"""


async def executor_agent_node(state: AgentState) -> AgentState:
    """Agente 3: El Juez de Riesgo (The Executor).

    Evalúa objetivamente los argumentos del Estratega y el Abogado del Diablo,
    considera la posición actual del portfolio, y toma la decisión final.

    Es frío, equilibrado y no toma partido - solo evalúa la fuerza de los argumentos.

    Contract:
    - Input: estado con propuesta del Estratega + crítica del Abogado del Diablo.
    - Output: mismo estado, agregando:
        - `executor_decision` (str): "buy" | "sell" | "hold"
        - `executor_reasoning` (str): razonamiento de la decisión
        - `executor_final_params` (dict): parámetros adicionales
      o `error_message` si algo falla.

    Regla LangGraph: siempre devolver el mismo objeto/Tipo de estado.
    """

    logger.info("⚖️ Agente 3 (El Juez) iniciando evaluación...")

    # Verificar que tenemos las propuestas de ambos agentes
    if not state.get("strategist_direction"):
        state["error_message"] = "No hay propuesta del Estratega para evaluar"
        return state

    if not state.get("skeptic_recommendation"):
        state["error_message"] = "No hay crítica del Abogado del Diablo para evaluar"
        return state

    # 1. Obtener posición actual del portfolio
    symbol = state.get("symbols", ["BTCUSD"])[0]

    try:
        position = await _get_current_position_context(symbol)
    except Exception as exc:
        logger.error(f"Error obteniendo posición actual: {exc}", exc_info=True)
        state["error_message"] = f"Error al consultar posición: {str(exc)}"
        return state

    # 2. Construir contextos
    position_text = _build_position_context_text(position, symbol)
    debate_text = _build_debate_summary(state)

    # 3. Crear prompt para el LLM
    system_prompt = """Eres "El Juez de Riesgo" (The Executor), el Agente 3 del Trading Committee.

TU PERSONALIDAD:
- Eres FRÍO y EQUILIBRADO - no tomas partido
- Tu único trabajo es EVALUAR OBJETIVAMENTE los argumentos de ambos agentes
- Eres el DECISOR FINAL - tu palabra es la última
- No eres ni optimista ni pesimista - eres RACIONAL

TU TRABAJO:
1. Evaluar los argumentos del ESTRATEGA (optimista)
2. Evaluar los argumentos del ABOGADO DEL DIABLO (pesimista)
3. Considerar la POSICIÓN ACTUAL del portfolio
4. Tomar la decisión final: BUY, SELL o HOLD

REGLAS CRÍTICAS SOBRE LA POSICIÓN:
- Si ya tienes POSICIÓN ABIERTA y el Estratega dice "buy" → Considerar HOLD
- Si NO tienes posición y el Estratega dice "buy" + riesgos bajos → Considerar BUY
- Si tienes posición y el Abogado del Diablo identifica riesgos críticos → Considerar SELL
- Si tienes posición y consideras que el precio seguira subiendo→ Considerar HOLD

LÓGICA DE DECISIÓN:
- BUY: Solo si NO tienes posición + argumentos del Estratega son fuertes + riesgos son manejables
- SELL: Solo si TIENES posición + riesgos críticos identificados por el Abogado del Diablo
- HOLD: Solo si tiene una posicion y consideres que el precio seguira subiendo

EVALUACIÓN:
1. ¿Qué argumentos del Estratega son VÁLIDOS?
2. ¿Qué riesgos del Abogado del Diablo son REALES?
3. ¿Cuál es la posición actual? (critical factor)
4. ¿Cuál es el balance de riesgo/oportunidad?

IMPORTANTE:
- Sé OBJETIVO - no favorezcas a ninguno
- Considera AMBOS lados del argumento
- La posición actual es FACTOR CRÍTICO
- Explica claramente por qué aceptas/rechazas cada argumento
- Tu decisión debe ser COHERENTE con la posición actual
- prioriza materializar las ganancias

Devuelve SOLO un JSON con el formato especificado."""

    user_prompt = f"""Como Juez imparcial, evalúa este caso y toma la decisión final:

{position_text}

{debate_text}

INSTRUCCIÓN:
Evalúa objetivamente ambos argumentos, considera la posición actual (CRÍTICO), 
y decide: BUY, SELL o HOLD.

Recuerda:
- Si ya tienes posición → HOLD o SELL 
- Si no tienes posición → BUY o HOLD
."""

    # 4. Ejecutar con AgentExecutor
    try:
        decision = await agent_executor.execute(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            response_model=ExecutorDecision,
            context={
                "agent": "executor",
                "symbol": symbol,
                "has_position": position["has_position"],
            },
        )
    except AgentExecutorError as exc:
        logger.error(f"Error ejecutando Agente Juez: {exc}", exc_info=True)
        state["error_message"] = f"Error en Agente Juez: {str(exc)}"
        return state

    # 5. Validar coherencia de la decisión con la posición
    if decision.final_decision == "buy" and position["has_position"]:
        logger.warning(
            "⚠️ El Juez sugirió BUY pero ya hay posición - cambiando a HOLD por seguridad"
        )
        decision.final_decision = "hold"
        decision.reasoning = f"[AJUSTADO POR SEGURIDAD] {decision.reasoning}\n\nNOTA: La decisión original era BUY, pero se cambió a HOLD porque ya existe una posición abierta. Evitamos sobreexposición."

    if decision.final_decision == "sell" and not position["has_position"]:
        logger.warning(
            "⚠️ El Juez sugirió SELL pero no hay posición - cambiando a HOLD"
        )
        decision.final_decision = "hold"
        decision.reasoning = f"[AJUSTADO POR SEGURIDAD] {decision.reasoning}\n\nNOTA: La decisión original era SELL, pero se cambió a HOLD porque no hay posición para vender."

    # 6. Asignar resultados al estado
    state["executor_decision"] = decision.final_decision
    state["executor_reasoning"] = decision.reasoning

    state["executor_final_params"] = {
        "risk_assessment": decision.risk_assessment,
        "confidence_level": decision.confidence_level,
        "position_context_considered": decision.position_context_considered,
        "has_current_position": position["has_position"],
        "current_quantity": position["current_quantity"],
        "available_usd": position["available_usd"],
    }

    # Construir texto completo de la decisión
    strategist_points_text = "\n".join(
        [f"    ✓ {p}" for p in decision.strategist_points_accepted]
    )
    skeptic_points_text = "\n".join(
        [f"    ✓ {p}" for p in decision.skeptic_points_accepted]
    )
    key_factors_text = "\n".join(
        [f"    • {f}" for f in decision.key_factors_for_decision]
    )

    state["executor_decision_text"] = f"""
⚖️ DECISIÓN FINAL DEL JUEZ

🎯 DECISIÓN: {decision.final_decision.upper()}

📊 Posición Actual: {'SÍ - Ya tienes posición' if position['has_position'] else 'NO - Sin posición'}
⚠️  Evaluación de Riesgo: {decision.risk_assessment.upper()}
💯 Confianza: {decision.confidence_level.upper()}

📝 RAZONAMIENTO:
{decision.reasoning}

✅ ARGUMENTOS DEL ESTRATEGA ACEPTADOS:
{strategist_points_text}

⚠️  ARGUMENTOS DEL ABOGADO DEL DIABLO ACEPTADOS:
{skeptic_points_text}

🔑 FACTORES CLAVE PARA LA DECISIÓN:
{key_factors_text}
"""

    # Limpieza de error si todo fue bien
    if state.get("error_message"):
        state["error_message"] = None

    logger.info(
        f"✅ Agente Juez completado: {decision.final_decision.upper()} "
        f"(riesgo: {decision.risk_assessment}, confianza: {decision.confidence_level})"
    )

    return state

