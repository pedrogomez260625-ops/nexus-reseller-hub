"""
Nexus Reseller Core - Anonymous Configuration Module
System: Ghost Reseller Gateway
"""

from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    SYSTEM_NAME: str = "Nexus Reseller Core"
    VERSION: str = "2.0.0"
    DEBUG: bool = False

    # Upstream Provider Configuration (Bunny Tools)
    RESELLER_API_KEY: Optional[str] = "YOUR_BUNNY_API_KEY"
    RESELLER_BASE_URL: str = "https://bhao.site/api/reseller/v1"
    DEFAULT_MARKUP_USDT: float = 3.0

    # Telegram Bot Configuration
    TELEGRAM_BOT_TOKEN: Optional[str] = "YOUR_TELEGRAM_BOT_TOKEN"
    ADMIN_TELEGRAM_ID: Optional[int] = 1849945160

    # Billeteras de Cobro (Pedro Gomez / MetaMask)
    DEPOSIT_WALLET_BSC: str = "0xe733e832e20cAE3a1e897F7F4A5B6e16934675C9"
    DEPOSIT_WALLET_TRON: str = "TZ3DYd7HNhnnSYUfris5Pqm66YmDugQ5Ch"
    DEPOSIT_WALLET_BTC: str = "bc1qt3s56f8h4crf69httj2snvseq5q6lskpnn5w64"
    DEPOSIT_WALLET_SOL: str = "cjwdWUXMtHgNU4dQmWEKPuyYLm4eonxpfyjhL6crCu4"

    # Billeteras Mayoristas Bunny
    SUPPLIER_WALLET_BSC: str = "0xec0183f1411c106afb8cfe32c391fef536f681d4"
    SUPPLIER_WALLET_TRON: str = "TKuRmAYaCQR3nTv3M8XtRZ8VwXfuLHWPbE"

    # Webhook / Runtime
    RUN_MODE: str = "webhook"
    WEBHOOK_URL: str = "https://nexus-reseller-hub.onrender.com/webhook"
    DATABASE_PATH: str = "ghost_reseller_wallet.db"

settings = Settings()
