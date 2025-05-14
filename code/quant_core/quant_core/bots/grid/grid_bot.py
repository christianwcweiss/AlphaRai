# pylint: disable=R0801
import asyncio
from enum import Enum
from typing import List, Dict, Any

from quant_core.bots.bots import BaseTradingBot
from quant_core.services.core_logger import CoreLogger
from quant_core.trader.trader import Trader


class GridTradingBotMode(Enum):
    """
    Enum for grid trading bot modes.
    """

    LONG = "long"
    SHORT = "short"
    LONG_SHORT = "long_short"
    TREND_ADAPTIVE = "trend_adaptive"


class GridTradingBot(BaseTradingBot):
    """
    A basic grid trading bot. Places a series of limit buy/sell orders around the current price.
    Replaces filled orders to maintain the grid.
    """

    __ALLOW_MULTIPLE_SYMBOLS__ = False

    def __init__(  # pylint: disable=too-many-arguments,too-many-positional-arguments
        self,
        bot_id: str,
        trader: Trader,
        symbols: List[str],
        bottom_level: float,
        top_level: float,
        grid_levels: int,
        order_size: float,
        mode: GridTradingBotMode,
    ) -> None:
        super().__init__(bot_id=bot_id, trader=trader, symbols=symbols)
        self._bottom_level = bottom_level
        self._top_level = top_level
        self._levels = grid_levels
        self._spacing = (top_level - bottom_level) / grid_levels
        self._order_size = order_size
        self._mode = mode

    @property
    def bottom_level(self) -> float:
        """Bottom level of the grid."""
        return self._bottom_level

    @property
    def top_level(self) -> float:
        """Top level of the grid."""
        return self._top_level

    @property
    def levels(self) -> int:
        """Number of levels in the grid."""
        return self._levels

    @property
    def spacing(self) -> float:
        """Spacing between levels in the grid."""
        return self._spacing

    @property
    def order_size(self) -> float:
        """Size of each order in the grid."""
        return self._order_size

    @property
    def mode(self) -> GridTradingBotMode:
        """Mode of the grid trading bot."""
        return self._mode

    def risk_per_grid(self, lot_size: float) -> float:
        """
        Calculates the risk per grid level based on the lot size.
        """
        return lot_size * self._order_size * self._spacing

    def _build_grid(self, symbol: str, mid_price: float) -> List[Dict[str, Any]]:
        """Build grid orders depending on the mode."""
        grid = []

        for i in range(1, self._levels + 1):
            offset = self._spacing * i

            if self._mode in [GridTradingBotMode.LONG, GridTradingBotMode.LONG_SHORT]:
                grid.append(
                    {"symbol": symbol, "side": "buy", "price": round(mid_price - offset, 5), "size": self._order_size}
                )

            if self._mode in [GridTradingBotMode.SHORT, GridTradingBotMode.LONG_SHORT]:
                grid.append(
                    {"symbol": symbol, "side": "sell", "price": round(mid_price + offset, 5), "size": self._order_size}
                )

            if self._mode == GridTradingBotMode.TREND_ADAPTIVE:
                raise NotImplementedError("Trend adaptive mode is not implemented yet.")

        return grid

    def _sync_grid(self, symbol: str) -> None:
        """Update the grid for a symbol."""
        raise NotImplementedError("Grid bot does not support sync grid yet.")

    async def bot_loop(self) -> None:
        CoreLogger().info("Grid bot loop started.")
        while True:
            try:
                for symbol in self.symbols:
                    self._sync_grid(symbol)
            except Exception as error:  # pylint: disable=broad-exception-caught
                CoreLogger().error(f"Grid bot error: {error}")

            await asyncio.sleep(30)

    def execute_trade(self, signal: Dict[str, Any], size: float) -> bool:
        CoreLogger().warning(f"Grid bot {self._bot_id} does not support manual trade execution.")
        raise NotImplementedError(f"Grid bot {self._bot_id} does not support trade execution (yet).")

    def close_all_positions(self) -> None:
        CoreLogger().info("Closing all open positions and cancelling orders.")
        raise NotImplementedError(f"Grid bot {self._bot_id} does not support closing positions directly. (yet)")
