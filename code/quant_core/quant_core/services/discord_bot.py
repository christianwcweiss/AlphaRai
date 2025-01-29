import requests

from quant_core.enums.discord_channels import DiscordChannel
from quant_core.services.core_logger import CoreLogger


class DiscordBot:
    def _send_to_discord(self, title: str, message: str, discord_channel: DiscordChannel) -> None:
        """Sends a log message to a Discord channel using a webhook."""

        webhook_url = discord_channel.get_webhook_url()

        if not webhook_url:
            CoreLogger().warning("DISCORD_WEBHOOK_URL is not set. Skipping Discord alert.")
            return

        payload = {
            "username": discord_channel.get_username(),
            "embeds": [
                {
                    "title": title,
                    "description": message,
                    "color": 0x8E44AD,
                }
            ],
        }

        try:
            response = requests.post(webhook_url, json=payload, timeout=5)
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            CoreLogger().error(f"Failed to send message to Discord: {e}")

    def send(self, title: str, message: str, discord_channel: DiscordChannel) -> None:
        self._send_to_discord(title, message, discord_channel)
