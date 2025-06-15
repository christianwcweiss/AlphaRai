from typing import Any, Dict

import pandas as pd
from quant_core.confluences.confluence import Confluence
from quant_core.enums.trade_direction import TradeDirection
from quant_core.features.indicators.nadaraya_watson_envelope import DataFeatureNadarayaWatsonEnvelope


class ConfluenceNadarayaWatsonEnvelopePosition(Confluence):
    """Confluence that scores how close the price is to the envelope bands relative to trade direction."""

    __NAME__ = "Nadaraya-Watson Envelope Position"
    __DESCRIPTION__ = (
        "Scores close to 1.0 if price is near the favorable envelope edge (upper for short, lower for long), "
        "0.0 if near the unfavorable edge. 0.5 if in the middle."
    )
    __IS_AUTOMATIC__ = True

    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self._bandwidth = config.get("bandwidth", 5.0)
        self._std_multiplier = config.get("std_multiplier", 2.0)

    def check(self, data_frame: pd.DataFrame, direction: TradeDirection) -> float:
        feature = DataFeatureNadarayaWatsonEnvelope(
            bandwidth=self._bandwidth,
            std_multiplier=self._std_multiplier,
        )

        data_frame = feature.add_feature(data_frame)
        data_frame = feature.normalize_feature(data_frame)

        _, upper_col, lower_col = feature.get_columns()

        if data_frame.empty or upper_col not in data_frame.columns or lower_col not in data_frame.columns:
            return 0.5

        normalized_upper = data_frame[upper_col].iloc[-1]
        normalized_lower = data_frame[lower_col].iloc[-1]

        if normalized_upper <= normalized_lower:
            return 0.5

        def scale(value: float, min_: float, max_: float) -> float:
            return max(0.0, min(1.0, (value - min_) / (max_ - min_)))

        price_pos = scale(0.0, normalized_lower, normalized_upper)

        if direction.normalize() is TradeDirection.LONG.normalize():
            return 1.0 - price_pos  # lower = 1.0, upper = 0.0
        if direction.normalize() is TradeDirection.SHORT.normalize():
            return price_pos  # upper = 1.0, lower = 0.0

        return 0.5

    def normalize(self, score: float, min_value: float, max_value: float) -> float:
        """Normalize score into a custom range."""
        return min_value + (max_value - min_value) * score
