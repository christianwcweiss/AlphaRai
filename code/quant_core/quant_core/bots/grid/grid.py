import asyncio
from typing import List, Dict, Any

from quant_core.bots.bots import BaseTradingBot
from quant_core.services.core_logger import CoreLogger


class GridTradingBot(BaseTradingBot):
    """
    A basic grid trading bot. Places a series of limit buy/sell orders around the current price.
    Replaces filled orders to maintain the grid.
    """

    def __init__(
        self,
        account_id: str,
        symbols: List[str],
        broker_client,  # Must implement `get_price`, `place_limit_order`, `get_open_orders`
        grid_spacing: float = 0.005,  # 0.5%
        grid_levels: int = 5,
        order_size: float = 0.1
    ):
        super().__init__(account_id, symbols)
        self._broker = broker_client
        self._spacing = grid_spacing
        self._levels = grid_levels
        self._order_size = order_size

    def _build_grid(self, symbol: str, mid_price: float) -> List[Dict[str, Any]]:
        """
        Builds a grid of buy/sell limit orders around the current mid price.
        """
        grid = []

        for i in range(1, self._levels + 1):
            offset = mid_price * self._spacing * i

            grid.append({
                "symbol": symbol,
                "side": "buy",
                "price": round(mid_price - offset, 5),
                "size": self._order_size
            })

            grid.append({
                "symbol": symbol,
                "side": "sell",
                "price": round(mid_price + offset, 5),
                "size": self._order_size
            })

        return grid

    def _sync_grid(self, symbol: str):
        """
        Builds the grid and submits limit orders. Maintains open orders only if price levels match.
        """
        current_price = self._broker.get_price(symbol)
        CoreLogger().info(f"[{self._account_id}] Current {symbol} price: {current_price}")

        target_orders = self._build_grid(symbol, current_price)
        open_orders = self._broker.get_open_orders(symbol)

        # Cancel any orders not matching the grid
        for o in open_orders:
            match = any(
                abs(o["price"] - t["price"]) < 1e-5 and o["side"] == t["side"]
                for t in target_orders
            )
            if not match:
                self._broker.cancel_order(o["order_id"])
                CoreLogger().info(f"Canceled outdated order {o['order_id']}")

        # Submit any missing grid orders
        for t in target_orders:
            match = any(
                abs(t["price"] - o["price"]) < 1e-5 and t["side"] == o["side"]
                for o in open_orders
            )
            if not match:
                order_id = self._broker.place_limit_order(
                    symbol=t["symbol"],
                    side=t["side"],
                    price=t["price"],
                    size=t["size"]
                )
                CoreLogger().info(f"Placed {t['side']} order at {t['price']} → ID: {order_id}")

    async def bot_loop(self):
        CoreLogger().info(f"[{self._account_id}] Grid bot loop started.")
        while True:
            try:
                for symbol in self._symbols:
                    self._sync_grid(symbol)
            except Exception as e:
                CoreLogger().error(f"Grid bot error: {e}")

            await asyncio.sleep(30)  # Grid refresh interval

    def execute_trade(self, signal: Dict[str, Any], size: float) -> bool:
        CoreLogger().warning("Grid bot does not support manual signal execution.")
        return False

    def close_all_positions(self) -> None:
        CoreLogger().info(f"[{self._account_id}] Closing all open positions and cancelling orders.")
        for symbol in self._symbols:
            self._broker.cancel_all_orders(symbol)
            self._broker.close_all_positions(symbol)
