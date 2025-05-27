import requests  # type: ignore

import json
import boto3
from quant_core.enums.discord_channels import DiscordChannel
from quant_core.services.core_logger import CoreLogger


class DiscordBot:  # pylint: disable=too-few-public-methods
    """Handles sending messages to Discord channels using the bot token and REST API."""

    def __init__(self) -> None:
        self._bot_token = self._get_token_from_secrets_manager("DISCORD_BOT_TOKEN")

    def _get_token_from_secrets_manager(self, secret_name: str) -> str:
        """Fetches the bot token from AWS Secrets Manager."""
        secretsmanager_client = boto3.client("secretsmanager")
        secret_value = secretsmanager_client.get_secret_value(SecretId=secret_name)
        if "SecretString" in secret_value:
            return json.loads(secret_value["SecretString"])["DISCORD_BOT_TOKEN"]
        raise ValueError(f"Secret {secret_name} does not contain a usable string.")

    def _send_to_discord(self, title: str, message: str, discord_channel: DiscordChannel) -> None:
        """Sends a message to a Discord channel using the bot token and REST API."""
        channel_id = discord_channel.get_channel_id()  # Must be implemented
        url = f"https://discord.com/api/v10/channels/{channel_id}/messages"

        headers = {"Authorization": f"Bot {self._bot_token}", "Content-Type": "application/json"}

        payload = {
            "content": f"**{title.strip()}**\n{message.strip()}",
        }

        try:
            response = requests.post(url, headers=headers, json=payload, timeout=5)
            response.raise_for_status()
            CoreLogger().info(f"Successfully sent message to Discord channel {channel_id}")
        except requests.exceptions.RequestException as e:
            CoreLogger().error(f"Failed to send message to Discord via Bot Token: {e}")

    def send(self, title: str, message: str, discord_channel: DiscordChannel) -> None:
        """Public method to send a message."""
        self._send_to_discord(title, message, discord_channel)
