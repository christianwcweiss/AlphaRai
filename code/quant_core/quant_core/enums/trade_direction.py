import platform
from enum import Enum
from typing import Any

from quant_core.enums.order_type import OrderType

import MetaTrader5 as mt5


class TradeDirection(Enum):
    """Trade direction enum."""

    LONG = "LONG"
    BUY = "BUY"
    NEUTRAL = "NEUTRAL"
    SHORT = "SHORT"
    SELL = "SELL"

    def to_mt5(self, order_type: OrderType) -> Any:
        """Convert TradeDirection to MetaTrader5 order type."""
        direction = self.normalize()
        if direction is TradeDirection.LONG:
            if order_type is OrderType.MARKET:
                return mt5.ORDER_TYPE_BUY
            if order_type is OrderType.LIMIT:
                return mt5.ORDER_TYPE_BUY_LIMIT
        if direction is TradeDirection.SHORT:
            if order_type is OrderType.MARKET:
                return mt5.ORDER_TYPE_SELL
            if order_type is OrderType.LIMIT:
                return mt5.ORDER_TYPE_SELL_LIMIT

        raise ValueError(f"Invalid TradeDirection: {self} in combination with OrderType: {order_type}")

    def normalize(self) -> "TradeDirection":
        """Differentiate between LONG/BUY and SHORT/SELL."""
        if self is TradeDirection.BUY or self is TradeDirection.LONG:
            return TradeDirection.LONG
        if self is TradeDirection.SELL or self is TradeDirection.SHORT:
            return TradeDirection.SHORT

        return self

    def reverse(self) -> "TradeDirection":
        """Reverse the trade direction."""
        if self.normalize() is TradeDirection.LONG.normalize():
            return TradeDirection.SHORT.normalize()
        if self.normalize() is TradeDirection.SHORT.normalize():
            return TradeDirection.LONG.normalize()

        return self
