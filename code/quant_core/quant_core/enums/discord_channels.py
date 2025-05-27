from enum import Enum


class DiscordChannel(Enum):
    """Discord channels for sending messages."""

    ALERT = "ALERT"
    FOREX_SIGNALS = "FOREX_SIGNALS"
    CRYPTO_SIGNALS = "CRYPTO_SIGNALS"
    STOCK_SIGNALS = "STOCK_SIGNALS"
    INDICES_SIGNALS = "INDICES_SIGNALS"

    def get_channel_id(self) -> str:
        """Get the Discord channel ID for the given channel."""
        return {
            DiscordChannel.CRYPTO_SIGNALS: "1341053733446090753",
            DiscordChannel.FOREX_SIGNALS: "1341053733060087961",
            DiscordChannel.STOCK_SIGNALS: "1341053686217965779",
        }[self]
