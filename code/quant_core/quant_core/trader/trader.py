from abc import ABC, abstractmethod
from typing import Any, Optional

from quant_core.enums.order_type import OrderType
from quant_core.enums.trade_direction import TradeDirection


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
        magic: Optional[int] = None,
        limit_level: Optional[float] = None,
        comment: Optional[str] = None,
    ) -> Any:
        """Open a position with the specified parameters."""
