import platform
from enum import Enum
from typing import Union, Any

from quant_core.enums.order_type import OrderType

if platform == "Windows":
    import MetaTrader5 as mt5
else:
    from unittest.mock import Mock

    mt5 = Mock()
    mt5.ORDER_TYPE_BUY = 0
    mt5.ORDER_TYPE_SELL = 1
    mt5.ORDER_TYPE_BUY_LIMIT = 2
    mt5.ORDER_TYPE_SELL_LIMIT = 3
    mt5.ORDER_TYPE_BUY_STOP = 4
    mt5.ORDER_TYPE_SELL_STOP = 5

class TradeDirection(Enum):
    LONG = "LONG"
    BUY = "BUY"
    SHORT = "SHORT"
    SELL = "SELL"

    def to_ig(self) -> str:
        if self is TradeDirection.LONG or self is TradeDirection.BUY:
            return "BUY"
        elif self is TradeDirection.SHORT or self is TradeDirection.SELL:
            return "SELL"
        else:
            raise ValueError(f"Invalid TradeDirection: {self}")

    def to_mt5(self, order_type: OrderType) -> Any:
        direction = self.normalize()
        if direction is TradeDirection.LONG:
            if order_type is OrderType.MARKET:
                return mt5.ORDER_TYPE_BUY
            elif order_type is OrderType.LIMIT:
                return mt5.ORDER_TYPE_BUY_LIMIT
        elif direction is TradeDirection.SHORT:
            if order_type is OrderType.MARKET:
                return mt5.ORDER_TYPE_SELL
            elif order_type is OrderType.LIMIT:
                return mt5.ORDER_TYPE_SELL_LIMIT

        raise ValueError(f"Invalid TradeDirection: {self} in combination with OrderType: {order_type}")

    def normalize(self) -> "TradeDirection":
        if self is TradeDirection.BUY:
            return TradeDirection.LONG
        elif self is TradeDirection.SELL:
            return TradeDirection.SHORT
        else:
            return self

    def reverse(self) -> "TradeDirection":
        if self is TradeDirection.LONG:
            return TradeDirection.SHORT
        elif self is TradeDirection.SHORT:
            return TradeDirection.LONG
        else:
            return self
