"""Script de prueba para el nodo de notificación por email."""

import asyncio
import logging

from app.agent.nodes.email_notification_node import send_email_notification_node
from app.agent.state.agent_state import AgentState

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)


async def test_email_notification():
    """Prueba el envío de email con un estado de ejemplo."""

    # Estado de prueba
    test_state: AgentState = {
        "symbols": ["BTCUSD"],
        "executor_decision": "buy",
        "executor_decision_text": """
=== DECISIÓN FINAL ===

Después de analizar toda la información disponible, he decidido:

ACCIÓN: COMPRAR (BUY)

JUSTIFICACIÓN:
1. Análisis técnico muestra tendencia alcista con golden cross
2. Sentimiento de noticias es positivo (80% positivo)
3. Fear & Greed Index en 65 (Greed moderado)
4. Precio cerca de soporte fuerte en $45,000

PARÁMETROS DE LA OPERACIÓN:
- Símbolo: BTCUSD
- Cantidad: 0.05 BTC
- Precio objetivo: $48,000
- Stop loss: $43,500
- Ratio riesgo/beneficio: 1:3

RIESGOS IDENTIFICADOS:
- Volatilidad de mercado alta
- Resistencia en $47,000
- Posible corrección después de subida

Esta decisión se toma con confianza del 75%.
        """.strip(),
        "news_limit": 10,
    }

    print("=" * 80)
    print("PRUEBA DE NOTIFICACIÓN POR EMAIL")
    print("=" * 80)
    print(f"\nEnviando email de prueba con estado:")
    print(f"Símbolos: {test_state['symbols']}")
    print(f"Decisión: {test_state['executor_decision']}")
    print(f"\nTexto de decisión:")
    print(test_state['executor_decision_text'])
    print("\n" + "=" * 80)
    print("Enviando email...")
    print("=" * 80 + "\n")

    # Ejecutar el nodo
    result_state = await send_email_notification_node(test_state)

    print("\n" + "=" * 80)
    if result_state.get("error_message"):
        print(f"❌ ERROR: {result_state['error_message']}")
    else:
        print("✅ Email enviado exitosamente!")
    print("=" * 80)


if __name__ == "__main__":
    asyncio.run(test_email_notification())

