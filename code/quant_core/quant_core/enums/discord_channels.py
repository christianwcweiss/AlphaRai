import os
from enum import Enum
from typing import Optional


class DiscordChannel(Enum):
    ALERT = "ALERT"
    FOREX_SIGNALS = "FOREX_SIGNALS"
    CRYPTO_SIGNALS = "CRYPTO_SIGNALS"
    STOCK_SIGNALS = "STOCK_SIGNALS"
    INDICES_SIGNALS = "INDICES_SIGNALS"

    def get_username(self) -> str:
        return os.environ.get("DISCORD_USERNAME", "Alpha Rai 🤖")

    def get_webhook_url(self) -> Optional[str]:
        return os.environ.get(f"DISCORD_WEBHOOK_URL_{self.name.upper()}", None)
