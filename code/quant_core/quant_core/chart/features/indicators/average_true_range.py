from typing import List

import numpy as np
import pandas as pd
from ta.volatility import AverageTrueRange

from quant_core.chart.feature import DataFeature
from quant_core.utils.chart_utils import check_df_sorted, check_enough_rows


class DataFeatureAverageTrueRange(DataFeature):
    def __init__(self, atr_period: int = 14) -> None:
        self._atr_period = atr_period

    def get_columns(self) -> List[str]:
        return [f"atr_{self._atr_period}"]

    def add_feature(self, data_frame: pd.DataFrame) -> pd.DataFrame:
        indicator_column_name = self.get_columns()[0]
        if indicator_column_name in data_frame:
            return data_frame

        check_df_sorted(data_frame=data_frame)
        check_enough_rows(data_frame=data_frame)

        data_frame[indicator_column_name] = AverageTrueRange(
            high=data_frame["high"], low=data_frame["low"], close=data_frame["close"], window=self._atr_period
        ).average_true_range()

        data_frame[indicator_column_name][: self._atr_period] = np.nan

        return data_frame

    def normalize_feature(self, data_frame: pd.DataFrame) -> pd.DataFrame:
        indicator_column_name = self.get_columns()[0]
        normalized_column_name = self.get_feature_columns()[0]
        data_frame[normalized_column_name] = data_frame[indicator_column_name] / data_frame["close"]

        return data_frame

    def get_feature_columns(self) -> List[str]:
        return [f"{self.get_columns()[0]}_normalized"]
