from typing import Optional, Any

from quant_core.clients.mt5.mt5_client import Mt5Client  # adjust path to where you placed Mt5Client

from quant_core.enums.order_type import OrderType
from quant_core.enums.trade_direction import TradeDirection
from quant_core.trader.trader import Trader


class Mt5Trader(Trader):
    def __init__(self, secret_id: str):
        self._mt5_client = Mt5Client(secret_id)

    def get_balance(self) -> float:
        return self._mt5_client.get_balance()

    def open_position(
        self,
        symbol: str,
        trade_direction: TradeDirection,
        order_type: OrderType,
        size: float,
        stop_loss: float,
        take_profit: float,
        limit_level: Optional[float] = None,
        comment: Optional[str] = None,
    ) -> Any:
        return self._mt5_client.send_order(
            symbol=symbol,
            trade_direction=trade_direction,
            order_type=order_type,
            size=size,
            stop_loss=stop_loss,
            take_profit=take_profit,
            limit_level=limit_level,
            comment=comment,
        )

    def shutdown(self) -> None:
        self._mt5_client.shutdown()
