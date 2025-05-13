from typing import Optional, Dict, Any

from quant_core.enums.time_period import TimePeriod
from quant_core.enums.trade_direction import TradeDirection


class TradeDetails:  # pylint: disable=too-many-instance-attributes
    """Class representing trade details."""

    def __init__(  # pylint: disable=too-many-arguments, too-many-positional-arguments
        self,
        symbol: str,
        direction: str,
        timeframe: str,
        entry: float,
        stop_loss: float,
        take_profit_1: float,
        take_profit_2: Optional[float] = None,
        take_profit_3: Optional[float] = None,
        ai_confidence: Optional[float] = None,
    ) -> None:
        self._symbol = symbol
        self._direction = TradeDirection(direction.upper())
        self._timeframe = int(timeframe)
        self._entry = entry
        self._stop_loss = stop_loss
        self._take_profit_1 = take_profit_1
        self._take_profit_2 = take_profit_2
        self._take_profit_3 = take_profit_3
        self._ai_confidence = ai_confidence

    @property
    def symbol(self) -> str:
        """Retrieves the symbol for the trade."""
        return self._symbol

    @property
    def direction(self) -> TradeDirection:
        """Retrieves the direction of the trade."""
        return self._direction

    @property
    def timeframe(self) -> TimePeriod:
        """Retrieves the timeframe for the trade."""
        return TimePeriod(int(self._timeframe))

    @property
    def entry(self) -> float:
        """Retrieves the entry level for the trade."""
        return self._entry

    @property
    def stop_loss(self) -> float:
        """Retrieves the stop loss level for the trade."""
        return self._stop_loss

    @property
    def take_profit_1(self) -> float:
        """Retrieves the first take profit level for the trade."""
        return self._take_profit_1

    @property
    def take_profit_2(self) -> Optional[float]:
        """Retrieves the second take profit level for the trade."""
        return self._take_profit_2

    @property
    def take_profit_3(self) -> Optional[float]:
        """Retrieves the third take profit level for the trade."""
        return self._take_profit_3

    @property
    def ai_confidence(self) -> Optional[float]:
        """Retrieves the AI confidence level for the trade."""
        return self._ai_confidence

    def to_dict(self) -> Dict[str, Any]:
        """Converts the trade details to a dictionary."""
        return {
            "symbol": self.symbol,
            "direction": self.direction.value,
            "timeframe": self.timeframe.value,
            "entry": self.entry,
            "stop_loss": self.stop_loss,
            "take_profit_1": self.take_profit_1,
            "take_profit_2": self.take_profit_2,
            "take_profit_3": self.take_profit_3,
            "ai_confidence": self.ai_confidence,
        }
