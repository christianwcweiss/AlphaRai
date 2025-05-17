from abc import ABC, abstractmethod
from typing import Optional, Any

from quant_core.enums.trade_direction import TradeDirection
from quant_core.enums.order_type import OrderType


class Trader(ABC):
    """Abstract base class for traders."""

    @abstractmethod
    def get_balance(self) -> float:
        """Get the account balance."""

    @abstractmethod
    def open_position(  # pylint: disable=too-many-arguments,too-many-positional-arguments
        self,
        symbol: str,
        trade_direction: TradeDirection,
        order_type: OrderType,
        size: float,
        stop_loss: float,
        take_profit: float,
        limit_level: Optional[float] = None,
    ) -> Any:
        """Open a position with the specified parameters."""
