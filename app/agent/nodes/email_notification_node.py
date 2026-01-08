"""Nodo final para enviar notificación por email con la decisión del ejecutor."""

import logging

from app.agent.state.agent_state import AgentState
from app.clients.email_client import email_client
from app.config.settings import settings

logger = logging.getLogger(__name__)


async def send_email_notification_node(state: AgentState) -> AgentState:
    """
    Nodo final que envía un email con la decisión del ejecutor.

    Este nodo toma el campo `executor_decision_text` del estado y lo envía
    por email al destinatario configurado en las settings.

    Args:
        state: Estado actual del agente con la decisión del ejecutor

    Returns:
        AgentState: Estado actualizado (mismo tipo que la entrada)
    """
    logger.info("🚀 Iniciando nodo de notificación por email")

    try:
        # Obtener el texto de decisión del estado
        decision_text = state.get("executor_decision_text")

        if not decision_text:
            logger.warning("No hay texto de decisión disponible para enviar por email")
            state["error_message"] = "No decision text available to send email"
            return state

        # Obtener información adicional para el email
        symbols = state.get("symbols", [])
        decision = state.get("executor_decision", "N/A")

        # Crear el asunto del email
        symbol_str = ", ".join(symbols) if symbols else "N/A"
        subject = f"🤖 SuperBot Trading Decision: {decision.upper()} - {symbol_str}"

        # Crear el cuerpo del email en texto plano
        body = f"""
SuperBot V2 - Trading Decision Notification
==========================================

Symbols: {symbol_str}
Decision: {decision.upper()}

Decision Details:
-----------------
{decision_text}

==========================================
This is an automated message from SuperBot V2
"""

        # Crear el cuerpo del email en HTML
        html_body = f"""
<!DOCTYPE html>
<html>
<head>
    <style>
        body {{
            font-family: Arial, sans-serif;
            line-height: 1.6;
            color: #333;
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
        }}
        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 20px;
            border-radius: 10px 10px 0 0;
        }}
        .content {{
            background: #f9f9f9;
            padding: 20px;
            border: 1px solid #ddd;
        }}
        .decision {{
            background: white;
            padding: 15px;
            border-left: 4px solid #667eea;
            margin: 15px 0;
        }}
        .footer {{
            background: #333;
            color: #999;
            padding: 15px;
            text-align: center;
            border-radius: 0 0 10px 10px;
            font-size: 12px;
        }}
        .badge {{
            display: inline-block;
            padding: 5px 10px;
            border-radius: 5px;
            font-weight: bold;
            margin: 5px 0;
        }}
        .badge-buy {{ background: #4caf50; color: white; }}
        .badge-sell {{ background: #f44336; color: white; }}
        .badge-hold {{ background: #ff9800; color: white; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>🤖 SuperBot V2 Trading Decision</h1>
    </div>
    <div class="content">
        <p><strong>Symbols:</strong> {symbol_str}</p>
        <p><strong>Decision:</strong> 
            <span class="badge badge-{decision.lower()}">{decision.upper()}</span>
        </p>
        
        <div class="decision">
            <h3>📊 Decision Details:</h3>
            <pre style="white-space: pre-wrap; font-family: monospace; font-size: 14px;">{decision_text}</pre>
        </div>
    </div>
    <div class="footer">
        <p>This is an automated message from SuperBot V2</p>
        <p>Do not reply to this email</p>
    </div>
</body>
</html>
"""

        # Enviar el email
        recipient = settings.aws_ses_recipient_email
        success = await email_client.send_email(
            to_email=recipient,
            subject=subject,
            body=body,
            html_body=html_body
        )

        if success:
            logger.info(f"✅ Email de notificación enviado exitosamente a {recipient}")
        else:
            logger.error(f"❌ Error al enviar email de notificación a {recipient}")
            state["error_message"] = "Failed to send email notification"

    except Exception as e:
        error_msg = f"Error en nodo de notificación por email: {str(e)}"
        logger.error(error_msg, exc_info=True)
        state["error_message"] = error_msg

    return state

