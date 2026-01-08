
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Settings:
    """Aplicación principal y configuración de clientes externos (Alpaca, etc.)."""

    app_name: str = "SuperBotV2"

    # Alpaca News API
    alpaca_news_base_url: str = "https://data.alpaca.markets"
    alpaca_api_key: str  = os.getenv("ALPACA_API_KEY",  "")
    alpaca_api_secret: str = os.getenv("ALPACA_API_SECRET", "")

    alpaca_news_timeout: float = 10.0
    alpaca_max_keepalive_connections: int = 20
    alpaca_max_connections: int = 50
    alpaca_keepalive_expiry: float = 30.0

    # Alpaca Crypto Bars API (mismo host, pero separados por claridad)
    alpaca_crypto_bars_timeout: float = 10.0

    # Polygon Indicators API
    indicators_base_url: str = "https://api.polygon.io"
    indicators_api_key: str = "zCuPu78iTz0unE5W0hd9i_gw9GO9d0LP"
    indicators_timeout: float = 10.0

    # Alternative.me Fear & Greed Index API
    fear_greed_base_url: str = "https://api.alternative.me"
    fear_greed_timeout: float = 10.0

    # OpenAI / LLM
    openai_api_key: str = os.getenv("OPENAI_API_KEY",  "")
    llm_model: str = "gpt-4o-mini"
    llm_temperature: float = 0.2
    llm_request_timeout: float = 15.0
    llm_max_retries: int = 1

    # MySQL Database
    mysql_host: str = "database-1.cqnjlktf7qpf.us-east-1.rds.amazonaws.com"
    mysql_port: int = 3306
    mysql_user: str = "admin"
    mysql_password: str = os.getenv("MYSQL_PASSWORD",  "")
    mysql_database: str = "superbot"
    mysql_pool_size: int = 5
    mysql_max_overflow: int = 10
    mysql_pool_timeout: float = 30.0
    mysql_pool_recycle: int = 3600  # Recycle connections after 1 hour

    # AWS SES Email Configuration
    aws_ses_host: str = "email-smtp.us-east-1.amazonaws.com"
    aws_ses_port: int = 587
    aws_ses_username: str = "AKIAV7LYMC73ZKMUJVJK"
    aws_ses_password: str = "BJ/Q43gzUCZJsKwS2lpldr7jO5o05sFf200ilLHonQ2W"
    # IMPORTANTE: Debe ser un email verificado en AWS SES
    # Para verificar un email: AWS Console -> SES -> Verified Identities -> Create Identity
    aws_ses_from_email: str = os.getenv("AWS_SES_FROM_EMAIL", "contacto@tuconsorciodigital.com")
    aws_ses_recipient_email: str = "marcoscanette1@gmail.com"
    aws_ses_use_tls: bool = True

    model_config = {
        "env_file": ".env",
        "case_sensitive": False,
    }


settings = Settings()
