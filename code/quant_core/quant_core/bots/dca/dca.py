from typing import Dict, Any, List
import asyncio

from quant_core.bots.bots import BaseTradingBot
from quant_core.services.core_logger import CoreLogger


class DcaTradingBot(BaseTradingBot):
    """
    Dollar-Cost Averaging (DCA) bot that buys a symbol in chunks as price drops.
    Useful for long-term accumulation or volatility dips.
    """

    def __init__(
        self,
        account_id: str,
        symbols: List[str],
        broker_client,
        dca_levels: int = 5,
        price_spacing: float = 0.01,  # 1% drop per level
        order_size: float = 0.1,
        max_position: float = 1.0
    ):
        super().__init__(account_id, symbols)
        self._broker = broker_client
        self._levels = dca_levels
        self._spacing = price_spacing
        self._order_size = order_size
        self._max_position = max_position
        self._active_orders = {}

    def _place_dca_grid(self, symbol: str):
        price = self._broker.get_price(symbol)
        orders = []

        for i in range(self._levels):
            level_price = round(price * (1 - self._spacing * i), 5)
            orders.append({
                "symbol": symbol,
                "side": "buy",
                "price": level_price,
                "size": self._order_size
            })

        # Cancel all existing DCA orders for this symbol
        self._broker.cancel_all_orders(symbol)

        # Place new grid
        for order in orders:
            order_id = self._broker.place_limit_order(
                symbol=order["symbol"],
                side=order["side"],
                price=order["price"],
                size=order["size"]
            )
            CoreLogger().info(f"[{symbol}] Placed DCA order: BUY {order['size']} @ {order['price']} (ID: {order_id})")

        self._active_orders[symbol] = orders

    def _check_position_limit(self, symbol: str) -> bool:
        pos = self._broker.get_position(symbol)
        if pos >= self._max_position:
            CoreLogger().warning(f"[{symbol}] Position {pos} exceeds max {self._max_position}. Skipping DCA.")
            return False
        return True

    async def bot_loop(self):
        CoreLogger().info(f"[{self._account_id}] DCA bot loop started.")
        while True:
            for symbol in self._symbols:
                try:
                    if self._check_position_limit(symbol):
                        self._place_dca_grid(symbol)
                except Exception as e:
                    CoreLogger().error(f"Error in DCA bot for {symbol}: {e}")

            await asyncio.sleep(60)  # Check once per minute

    def execute_trade(self, signal: Dict[str, Any], size: float) -> bool:
        CoreLogger().warning("DCA bot does not support signal-based trades.")
        return False

    def close_all_positions(self) -> None:
        CoreLogger().info(f"[{self._account_id}] Closing all positions and cancelling orders.")
        for symbol in self._symbols:
            self._broker.cancel_all_orders(symbol)
            self._broker.close_all_positions(symbol)
