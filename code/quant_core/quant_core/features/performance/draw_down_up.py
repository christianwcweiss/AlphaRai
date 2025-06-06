from typing import List

import pandas as pd
from quant_core.enums.trade_direction import TradeDirection
from quant_core.features.feature import DataFeature
from quant_core.utils.chart_utils import check_df_sorted, check_enough_rows


class DataFeatureDrawDownAndUp(DataFeature):
    """Data Feature for calculating draw down and draw up values."""

    def __init__(
        self,
        direction: TradeDirection,
        horizon: int = 1,
    ) -> None:
        self._original_direction = direction.normalize()
        self._reversed_direction = direction.normalize().reverse()
        self._horizon = horizon

    def get_columns(self) -> List[str]:
        return [
            f"draw_down_{self._original_direction.value.lower()}_{self._horizon}",
            f"draw_up_{self._original_direction.value.lower()}_{self._horizon}",
        ]

    def add_feature(self, data_frame: pd.DataFrame) -> pd.DataFrame:
        draw_down_column, draw_up_column = self.get_columns()
        if all(col in data_frame.columns for col in (draw_down_column, draw_up_column)):
            return data_frame

        check_df_sorted(data_frame=data_frame)
        check_enough_rows(data_frame=data_frame)

        rolling_min_low = data_frame["low"].rolling(self._horizon + 1).min()
        rolling_max_high = data_frame["high"].rolling(self._horizon + 1).max()

        if self._original_direction is TradeDirection.LONG:
            data_frame[draw_down_column] = rolling_min_low - data_frame["close"]
            data_frame[draw_up_column] = rolling_max_high - data_frame["close"]
        else:
            data_frame[draw_down_column] = rolling_max_high - data_frame["close"]
            data_frame[draw_up_column] = rolling_min_low - data_frame["close"]

        return data_frame

    def normalize_feature(self, data_frame: pd.DataFrame) -> pd.DataFrame:
        draw_down_column, draw_up_column = self.get_columns()
        draw_down_normalized_column, draw_up_normalized_column = self.get_feature_columns()

        data_frame[draw_down_normalized_column] = data_frame[draw_down_column] / data_frame["close"]
        data_frame[draw_up_normalized_column] = data_frame[draw_up_column] / data_frame["close"]

        return data_frame

    def get_feature_columns(self) -> List[str]:
        return [column + "_normalized" for column in self.get_columns()]
