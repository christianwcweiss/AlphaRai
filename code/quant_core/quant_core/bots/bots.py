from abc import ABC, abstractmethod
from typing import Any, Dict, List


class BaseTradingBot(ABC):
    """
    Abstract base class for a trading bot.
    Defines the required interface for implementing concrete trading bots.
    """

    def __init__(self, account_id: str, symbols: List[str]):
        """
        Initialize the bot with optional configuration.
        """
        self._account_id = account_id
        self._symbols = symbols

    @abstractmethod
    def bot_loop(self) -> None:
        """
        Main loop for the bot.
        This method should be overridden in subclasses to implement the bot's logic.
        """
        pass


    @abstractmethod
    def execute_trade(self, signal: Dict[str, Any], size: float) -> bool:
        """
        Send the trade order to the broker.
        Returns True if the trade was placed successfully.
        """
        pass


    @abstractmethod
    def close_all_positions(self) -> None:
        """
        Force-close all open positions (e.g., during shutdown or risk event).
        """
        pass

