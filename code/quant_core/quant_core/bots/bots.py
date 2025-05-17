from abc import ABC, abstractmethod
from typing import Any, Dict, List

from quant_core.trader.trader import Trader


class BaseTradingBot(ABC):
    """
    Abstract base class for a trading bot.
    Defines the required interface for implementing concrete trading bots.
    """

    __ALLOW_MULTIPLE_SYMBOLS__: bool

    def __init__(self, bot_id: str, trader: Trader, symbols: List[str]) -> None:
        """
        Initialize the bot with optional configuration.
        """
        self._bot_id = bot_id
        self._trader = trader
        self._symbols = symbols
        if not self.__ALLOW_MULTIPLE_SYMBOLS__:
            raise ValueError("Validation failed: __ALLOW_MULTIPLE_SYMBOLS__ must be set in the subclass.")
        if not self.__ALLOW_MULTIPLE_SYMBOLS__ and len(symbols) > 1:
            raise ValueError("Multiple symbols are not allowed for this bot.")

    @property
    def bot_id(self) -> str:
        """Get the bot ID."""
        return self._bot_id

    @property
    def symbols(self) -> List[str]:
        """Get the list of symbols the bot is trading."""
        return self._symbols

    @abstractmethod
    async def bot_loop(self) -> None:
        """
        Main loop for the bot.
        This method should be overridden in subclasses to implement the bot's logic.
        """

    @abstractmethod
    def execute_trade(self, signal: Dict[str, Any], size: float) -> bool:
        """
        Send the trade order to the broker.
        Returns True if the trade was placed successfully.
        """

    @abstractmethod
    def close_all_positions(self) -> None:
        """
        Force-close all open positions (e.g., during shutdown or risk event).
        """
