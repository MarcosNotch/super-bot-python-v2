# Configuración de Email con AWS SES

## ⚠️ Importante: Verificación de Email Requerida

Para que el sistema de notificaciones por email funcione, **DEBES verificar tu email en AWS SES** antes de poder enviar mensajes.

## 📋 Pasos para Verificar tu Email en AWS SES

### Opción 1: Usar AWS Console (Interfaz Web)

1. **Accede a AWS Console**
   - Ve a: https://console.aws.amazon.com/ses/
   - Asegúrate de estar en la región **US-EAST-1** (Norte de Virginia)

2. **Verifica tu Email**
   - En el menú lateral, haz clic en **"Verified identities"**
   - Haz clic en el botón **"Create identity"**
   - Selecciona **"Email address"**
   - Ingresa: `contacto@tuconsorciodigital.com`
   - Haz clic en **"Create identity"**

3. **Confirma tu Email**
   - AWS enviará un email de verificación a `contacto@tuconsorciodigital.com`
   - Abre la bandeja de entrada de ese email
   - Busca un email de **"Amazon Web Services"** con asunto: "Amazon SES Email Address Verification Request"
   - **Haz clic en el enlace de verificación** dentro del email
   - Verás un mensaje de confirmación: "Congratulations! You've successfully verified..."

4. **Verifica el Estado**
   - Vuelve a la consola de AWS SES
   - En "Verified identities", deberías ver `contacto@tuconsorciodigital.com` con estado **"Verified"** ✅

### Opción 2: Usar AWS CLI

```bash
# 1. Solicitar verificación
aws ses verify-email-identity \
  --email-address contacto@tuconsorciodigital.com \
  --region us-east-1

# 2. Revisa tu email y haz clic en el enlace de verificación

# 3. Verificar el estado
aws ses get-identity-verification-attributes \
  --identities contacto@tuconsorciodigital.com \
  --region us-east-1
```

## 🧪 Probar el Sistema de Email

Una vez que hayas verificado tu email, puedes probar el sistema:

```bash
cd /Users/naranjax/PycharmProjects/SuperBotV2
python test_email_notification.py
```

Deberías ver:
```
✅ Email enviado exitosamente!
```

Y recibir un email en `marcoscanette1@gmail.com` con la decisión de trading.

## 📧 Configuración del Email

La configuración de email está en `app/config/settings.py`:

```python
# Email del remitente (debe estar verificado en AWS SES)
aws_ses_from_email: str = os.getenv("AWS_SES_FROM_EMAIL", "contacto@tuconsorciodigital.com")

# Email del destinatario
aws_ses_recipient_email: str = "marcoscanette1@gmail.com"
```

### Cambiar el Email del Remitente

Para usar un email diferente como remitente:

1. Verifica el email en AWS SES (pasos anteriores)
2. Crea/edita el archivo `.env`:
   ```bash
   AWS_SES_FROM_EMAIL=tu-email-verificado@ejemplo.com
   ```

## 🔒 Cuenta AWS SES en Sandbox

**IMPORTANTE**: Si tu cuenta de AWS SES está en modo "Sandbox" (nuevo por defecto), solo puedes enviar emails a:
- Emails verificados en SES
- Emails de prueba registrados

Para enviar emails a cualquier dirección:
1. Ve a: https://console.aws.amazon.com/ses/
2. En el menú lateral, haz clic en **"Account dashboard"**
3. Busca la sección **"Sending statistics"**
4. Si dice **"Sandbox"**, haz clic en **"Request production access"**
5. Completa el formulario explicando tu caso de uso

## 🚀 Integración con el Grafo de Trading

El nodo de email está integrado automáticamente en el grafo de trading:

```
Strategist → Skeptic → Executor → Email Notification → END
```

Cada vez que el agente ejecutor tome una decisión final, se enviará automáticamente un email con:
- La decisión (BUY, SELL, HOLD)
- El razonamiento completo
- Los factores considerados
- El contexto del mercado

## 🎨 Formato del Email

El email incluye:
- **Asunto**: `🤖 SuperBot Trading Decision: {DECISION} - {SYMBOL}`
- **Formato HTML**: Con colores y estilos profesionales
- **Formato Texto Plano**: Como fallback para clientes que no soportan HTML

## 🐛 Troubleshooting

### Error: "Email address is not verified"
**Solución**: Verifica el email del remitente en AWS SES (ver pasos arriba)

### Error: "MessageRejected: Email address is not verified"
**Solución**: Si estás en Sandbox, también debes verificar el email del destinatario

### Error: "Daily sending quota exceeded"
**Solución**: En Sandbox, el límite es 200 emails/día. Solicita acceso a producción.

### Error: "Invalid SMTP credentials"
**Solución**: Verifica que las credenciales en `settings.py` sean correctas

## 📚 Referencias

- [AWS SES - Getting Started](https://docs.aws.amazon.com/ses/latest/dg/send-email-smtp.html)
- [AWS SES - Verifying Identities](https://docs.aws.amazon.com/ses/latest/dg/verify-addresses-and-domains.html)
- [AWS SES - Moving Out of Sandbox](https://docs.aws.amazon.com/ses/latest/dg/request-production-access.html)

