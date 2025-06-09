from services.relay_bot import DiscordRelayBot


class TestDiscordRelayBot:
    def test_relay_bot_initialization(self) -> None:
        relay_bot = DiscordRelayBot()
        other_relay_bot = DiscordRelayBot()

        assert relay_bot is not None, "Relay bot should be initialized"
        assert relay_bot is other_relay_bot, "Relay bot should be a singleton instance"
