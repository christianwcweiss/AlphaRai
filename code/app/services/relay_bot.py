import asyncio
import json
import os
import tempfile
import threading
from datetime import UTC, datetime, timedelta
from typing import Any, Set

import boto3
import botocore.exceptions
import discord
import psutil
from models.cache.signals import Signal
from quant_core.services.core_logger import CoreLogger
from services.db.cache.signals import SignalService
from services.trade_parser import TradeMessageParser
from services.trade_router import TradeRouter

intents = discord.Intents.default()
intents.message_content = True

ALPHA_RAI_CHANNEL_IDS = [
    "1341053733446090753",
    "1341053733060087961",
    "1341053686217965779",
    "1378814931675250718",
]
ALPHA_RAI_WEBHOOKS_USER_IDS = [
    "116820183460347905",  # admin
    "1376589114417352774",  # bot
]


class DiscordRelayBot:
    """Singleton class for managing a Discord bot that relays messages to the local app."""

    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super().__new__(cls)
                cls._instance._initialized = False
            return cls._instance

    def __init__(self) -> None:
        if self._initialized:
            return
        self._initialized = True

        self._lockfile_path = os.path.join(tempfile.gettempdir(), "alpha_rai_bot.lock")

        try:
            self._token = json.loads(self._get_credentials_from_secrets_manager("DISCORD_BOT_TOKEN"))[
                "DISCORD_BOT_TOKEN"
            ]
        except (ValueError, botocore.exceptions.ClientError) as error:
            CoreLogger().error(f"Failed to load Discord bot token from secrets manager: {error}")
            CoreLogger().warning("Automatic trading will be disabled due to missing credentials.")
            self._token = None

        self._processed_message_ids: Set[str] = set()
        self._thread = None
        self._loop = None
        self._client = None
        self._running = False
        self._on_ready_ran = False

    def _get_credentials_from_secrets_manager(self, secret_name: str) -> str:
        secretsmanager_client = boto3.client("secretsmanager")
        secret_value = secretsmanager_client.get_secret_value(SecretId=secret_name)
        if "SecretString" in secret_value:
            return secret_value["SecretString"]
        raise ValueError(f"Secret {secret_name} not found.")

    def _lockfile_exists(self) -> bool:
        if not os.path.exists(self._lockfile_path):
            return False
        try:
            with open(self._lockfile_path, "r") as f:
                pid = int(f.read().strip())
            if psutil.pid_exists(pid):
                return True
            else:
                os.remove(self._lockfile_path)
                return False
        except Exception:
            os.remove(self._lockfile_path)
            return False

    def _create_lockfile(self):
        with open(self._lockfile_path, "w") as f:
            f.write(str(os.getpid()))

    def _remove_lockfile(self):
        if os.path.exists(self._lockfile_path):
            os.remove(self._lockfile_path)

    def _build_client(self):
        client = discord.Client(intents=intents)

        @client.event
        async def on_ready() -> None:
            if self._on_ready_ran:
                CoreLogger().debug("on_ready() already ran once — skipping duplicate execution.")
                return

            self._on_ready_ran = True
            self._running = True

            CoreLogger().info(f"Logged in as {client.user}")
            CoreLogger().info(f"Connected to {len(client.guilds)} server(s):")
            for guild in client.guilds:
                CoreLogger().info(f"Guild: {guild.name} (ID: {guild.id})")
                for channel in guild.text_channels:
                    CoreLogger().info(f"Channel: {channel.name} (ID: {channel.id})")

        @client.event
        async def on_disconnect():
            CoreLogger().warning("Discord bot disconnected... waiting to reconnect.")

        @client.event
        async def on_message(message: Any) -> None:
            CoreLogger().info(
                f"Received message from {message.author.name}/{message.author.id} "
                f"in {message.channel.name}: {message.content}"
            )

            if str(message.author.id) not in ALPHA_RAI_WEBHOOKS_USER_IDS:
                return
            if str(message.channel.id) not in ALPHA_RAI_CHANNEL_IDS:
                return
            if message.id in self._processed_message_ids:
                CoreLogger().debug(f"Duplicate message {message.id} ignored.")
                return

            self._processed_message_ids.add(message.id)
            if len(self._processed_message_ids) > 1000:
                self._processed_message_ids = set(list(self._processed_message_ids)[-500:])

            try:
                trade = TradeMessageParser().parse(message.content)
                CoreLogger().info(f"Parsed trade {trade} successfully received from Discord.")
                TradeRouter(trade=trade).route()
            except Exception as e:
                CoreLogger().error(f"Failed to parse and route trade: {e}")

        return client

    def download_all_messages(self):
        """Fetch and persist all historical trade messages from Discord."""

        async def _fetch_history():
            if not self._token:
                CoreLogger().warning("Bot cannot fetch history without a valid token.")
                return

            client = discord.Client(intents=intents)

            @client.event
            async def on_ready():
                CoreLogger().info("Starting historical message download...")

                SignalService().delete_all_signals()

                for guild in client.guilds:
                    for channel in guild.text_channels:
                        if str(channel.id) not in ALPHA_RAI_CHANNEL_IDS:
                            continue

                        CoreLogger().info(f"Fetching from channel: {channel.name} ({channel.id})")
                        seven_days_ago = datetime.now(UTC) - timedelta(days=7)

                        try:
                            async for message in channel.history(limit=None, after=seven_days_ago, oldest_first=True):
                                if str(message.author.id) not in ALPHA_RAI_WEBHOOKS_USER_IDS:
                                    continue
                                if message.id in self._processed_message_ids:
                                    continue

                                self._processed_message_ids.add(str(message.id))

                                try:
                                    trade = TradeMessageParser().parse(message.content)
                                    signal = Signal.from_parsed(trade, date=str(message.created_at))
                                    SignalService().store_signal(signal)
                                    CoreLogger().info(f"[HISTORY] Stored signal: {signal}")
                                except Exception as e:
                                    CoreLogger().error(f"[HISTORY] Failed to parse/store message {message.id}: {e}")
                        except Exception as e:
                            CoreLogger().error(f"Error in channel {channel.id}: {e}")

                CoreLogger().info("Finished downloading and storing historical messages.")
                await client.close()

            await client.start(self._token)

        CoreLogger().info("Running historical fetch now...")
        asyncio.run(_fetch_history())

    def run(self):
        """Start the Discord bot in a separate thread."""
        with self._lock:
            if self._lockfile_exists():
                CoreLogger().info("Bot lockfile exists and process is alive — skipping startup.")
                return
            if self._running:
                CoreLogger().debug("Bot already running — skipping thread start.")
                return
            if not self._token:
                CoreLogger().warning("Bot cannot start without a valid token.")
                return

            def start_bot():
                try:
                    self._loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(self._loop)
                    self._client = self._build_client()
                    self._loop.run_until_complete(self._client.start(self._token))
                except Exception as e:
                    CoreLogger().error(f"Bot crashed: {e}")
                finally:
                    self._running = False
                    self._remove_lockfile()
                    if self._loop and not self._loop.is_closed():
                        self._loop.run_until_complete(self._client.close())
                        self._loop.close()

            CoreLogger().info("Creating lockfile and starting Discord bot thread...")
            self._create_lockfile()
            self._thread = threading.Thread(target=start_bot, daemon=True)
            self._thread.start()

    def stop(self):
        """Stop the Discord bot if it is running."""
        if not self._running or not self._loop:
            CoreLogger().info("Bot is not running or no event loop available.")
            self._remove_lockfile()
            return

        CoreLogger().info("Stopping Discord bot...")
        self._remove_lockfile()
        asyncio.run_coroutine_threadsafe(self._client.close(), self._loop)

    def is_running(self) -> bool:
        """Return True if the lockfile exists and points to a live process."""
        return self._lockfile_exists()
