from typing import List, Dict, Any
import asyncio
import pandas as pd

from quant_core.bots.bots import BaseTradingBot
from quant_core.services.core_logger import CoreLogger


class MeanReversionGridBot(BaseTradingBot):
    """
    A grid bot that activates when price deviates from a statistical mean (SMA, EMA, VWAP).
    Trades around the mean expecting mean reversion.
    """

    def __init__(
        self,
        account_id: str,
        symbols: List[str],
        broker_client,
        data_fetcher,
        mean_type: str = "sma",  # or "ema", "vwap"
        mean_period: int = 50,
        deviation_trigger: float = 0.01,  # 1%
        grid_spacing: float = 0.002,
        grid_levels: int = 4,
        order_size: float = 0.1
    ):
        super().__init__(account_id, symbols)
        self._broker = broker_client
        self._fetcher = data_fetcher
        self._mean_type = mean_type
        self._mean_period = mean_period
        self._trigger = deviation_trigger
        self._spacing = grid_spacing
        self._levels = grid_levels
        self._size = order_size

    def _calculate_mean(self, df: pd.DataFrame) -> float:
        if self._mean_type == "sma":
            return df["close"].rolling(self._mean_period).mean().iloc[-1]
        elif self._mean_type == "ema":
            return df["close"].ewm(span=self._mean_period).mean().iloc[-1]
        elif self._mean_type == "vwap":
            vwap = (df["high"] + df["low"] + df["close"]) / 3
            return (vwap * df["volume"]).cumsum() / df["volume"].cumsum().iloc[-1]
        else:
            raise ValueError(f"Unsupported mean type: {self._mean_type}")

    def _build_grid(self, mean_price: float) -> List[Dict[str, Any]]:
        grid = []
        for i in range(1, self._levels + 1):
            offset = mean_price * self._spacing * i
            grid.append({"side": "buy", "price": round(mean_price - offset, 5), "size": self._size})
            grid.append({"side": "sell", "price": round(mean_price + offset, 5), "size": self._size})
        return grid

    def _sync_grid(self, symbol: str, current_price: float, mean_price: float):
        deviation = abs(current_price - mean_price) / mean_price
        if deviation < self._trigger:
            CoreLogger().info(f"[{symbol}] No grid triggered. Deviation {deviation:.4f} < {self._trigger}")
            return

        CoreLogger().info(f"[{symbol}] Price deviated {deviation:.2%} from {self._mean_type.upper()} mean. Building grid...")

        self._broker.cancel_all_orders(symbol)
        grid = self._build_grid(mean_price)

        for order in grid:
            order_id = self._broker.place_limit_order(
                symbol=symbol,
                side=order["side"],
                price=order["price"],
                size=order["size"]
            )
            CoreLogger().info(f"Placed {order['side']} order at {order['price']} (ID: {order_id})")

    async def bot_loop(self):
        CoreLogger().info(f"[{self._account_id}] Mean Reversion Grid bot started.")
        while True:
            for symbol in self._symbols:
                try:
                    df = self._fetcher.get_ohlcv(symbol, limit=self._mean_period + 10)  # returns pd.DataFrame
                    current_price = self._broker.get_price(symbol)
                    mean_price = self._calculate_mean(df)
                    self._sync_grid(symbol, current_price, mean_price)
                except Exception as e:
                    CoreLogger().error(f"Error in grid bot for {symbol}: {e}")

            await asyncio.sleep(30)

    def execute_trade(self, signal: Dict[str, Any], size: float) -> bool:
        CoreLogger().warning("Mean Reversion Grid bot does not support signal-based trades.")
        return False

    def close_all_positions(self) -> None:
        CoreLogger().info(f"[{self._account_id}] Closing all positions and cancelling orders.")
        for symbol in self._symbols:
            self._broker.cancel_all_orders(symbol)
            self._broker.close_all_positions(symbol)
