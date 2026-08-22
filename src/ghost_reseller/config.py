"""
Nexus Reseller Core - Anonymous Configuration Module
System: Ghost Reseller Gateway
"""

from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    SYSTEM_NAME: str = "Nexus Reseller Core"
    VERSION: str = "1.0.0"
    DEBUG: bool = False

    # Upstream Provider Configuration
    RESELLER_API_KEY: Optional[str] = None
    RESELLER_BASE_URL: str = "https://bhao.site/api/reseller/v1"
    DEFAULT_MARKUP_USDT: float = 3.0

    # Telegram Bot Configuration
    TELEGRAM_BOT_TOKEN: Optional[str] = None
    ADMIN_TELEGRAM_ID: Optional[int] = None

    # Payment Gateway
    CRYPTO_BOT_TOKEN: Optional[str] = None
    DATABASE_PATH: str = "ghost_reseller_wallet.db"

settings = Settings()
