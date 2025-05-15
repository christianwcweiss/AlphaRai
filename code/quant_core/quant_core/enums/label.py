from enum import Enum

from quant_core.enums.trade_direction import TradeDirection


class PredictionLabel(Enum):
    """Enum for prediction labels."""

    STRONG_BUY = 0
    BUY = 1
    NEUTRAL = 2
    SELL = 3
    STRONG_SELL = 4

    def to_trade_direction(self) -> TradeDirection:
        """Convert the prediction label to a trade direction."""
        if self is PredictionLabel.STRONG_BUY or self is PredictionLabel.BUY:
            return TradeDirection.LONG
        if self is PredictionLabel.SELL or self is PredictionLabel.STRONG_SELL:
            return TradeDirection.SHORT

        return TradeDirection.NEUTRAL
