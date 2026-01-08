"""Cliente para enviar emails usando AWS SES via SMTP."""

import logging
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import Optional

from app.config.settings import settings

logger = logging.getLogger(__name__)


class EmailClient:
    """Cliente singleton para enviar emails usando AWS SES."""

    def __init__(self):
        """Inicializar el cliente de email con configuración de AWS SES."""
        self.host = settings.aws_ses_host
        self.port = settings.aws_ses_port
        self.username = settings.aws_ses_username
        self.password = settings.aws_ses_password
        self.from_email = settings.aws_ses_from_email
        self.use_tls = settings.aws_ses_use_tls

    async def send_email(
        self,
        to_email: str,
        subject: str,
        body: str,
        html_body: Optional[str] = None
    ) -> bool:
        """
        Enviar un email usando AWS SES via SMTP.

        Args:
            to_email: Dirección de email del destinatario
            subject: Asunto del email
            body: Cuerpo del email en texto plano
            html_body: Cuerpo del email en HTML (opcional)

        Returns:
            bool: True si el email se envió correctamente, False en caso contrario

        Raises:
            Exception: Si ocurre un error al enviar el email
        """
        try:
            # Crear mensaje
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = self.from_email
            msg['To'] = to_email

            # Agregar cuerpo en texto plano
            part1 = MIMEText(body, 'plain', 'utf-8')
            msg.attach(part1)

            # Agregar cuerpo en HTML si está disponible
            if html_body:
                part2 = MIMEText(html_body, 'html', 'utf-8')
                msg.attach(part2)

            # Conectar al servidor SMTP y enviar
            with smtplib.SMTP(self.host, self.port) as server:
                if self.use_tls:
                    server.starttls()

                server.login(self.username, self.password)
                server.sendmail(self.from_email, to_email, msg.as_string())

            logger.info(f"Email enviado exitosamente a {to_email}")
            return True

        except Exception as e:
            logger.error(f"Error al enviar email a {to_email}: {str(e)}", exc_info=True)
            return False


# Instancia singleton del cliente
email_client = EmailClient()

