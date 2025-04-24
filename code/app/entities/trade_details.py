from dataclasses import dataclass
from typing import Optional, Dict, Any

from quant_core.enums.time_period import TimePeriod
from quant_core.enums.trade_direction import TradeDirection


class TradeDetails:
    def __init__(
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
        return self._symbol

    @property
    def direction(self) -> TradeDirection:
        return self._direction

    @property
    def timeframe(self) -> TimePeriod:
        return TimePeriod(int(self._timeframe))

    @property
    def entry(self) -> float:
        return self._entry

    @property
    def stop_loss(self) -> float:
        return self._stop_loss

    @property
    def take_profit_1(self) -> float:
        return self._take_profit_1

    @property
    def take_profit_2(self) -> Optional[float]:
        return self._take_profit_2

    @property
    def take_profit_3(self) -> Optional[float]:
        return self._take_profit_3

    @property
    def ai_confidence(self) -> Optional[float]:
        return self._ai_confidence


    def to_dict(self) -> Dict[str, Any]:
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