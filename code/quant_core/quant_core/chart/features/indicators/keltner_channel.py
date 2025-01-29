from typing import List

import pandas as pd
from ta.volatility import KeltnerChannel

from quant_core.chart.feature import DataFeature
from quant_core.utils.chart_utils import check_df_sorted, check_enough_rows


class DataFeatureKeltnerChannel(DataFeature):
    def __init__(self, kc_length: int = 20, kc_mult_factor: int = 2) -> None:
        self._kc_length = kc_length
        self._kc_mult_factor = kc_mult_factor

    def get_columns(self) -> List[str]:
        return [
            f"kc_mavg_{self._kc_length}_{self._kc_mult_factor}",
            f"kc_upper_{self._kc_length}_{self._kc_mult_factor}",
            f"kc_lower_{self._kc_length}_{self._kc_mult_factor}",
        ]

    def add_feature(self, data_frame: pd.DataFrame) -> pd.DataFrame:
        kc_mavg_column, kc_upper_column, kc_lower_column = self.get_columns()
        if all(col in data_frame.columns for col in {kc_mavg_column, kc_upper_column, kc_lower_column}):
            return data_frame

        check_df_sorted(data_frame=data_frame)
        check_enough_rows(data_frame=data_frame)

        kc = KeltnerChannel(
            high=data_frame["high"],
            low=data_frame["low"],
            close=data_frame["close"],
            window=self._kc_length,
            window_atr=self._kc_length,
            multiplier=self._kc_mult_factor,
            fillna=False,
        )
        data_frame[kc_mavg_column] = kc.keltner_channel_mband()
        data_frame[kc_upper_column] = kc.keltner_channel_hband()
        data_frame[kc_lower_column] = kc.keltner_channel_lband()

        return data_frame

    def normalize_feature(self, data_frame: pd.DataFrame) -> pd.DataFrame:
        kc_mavg, kc_upper, kc_lower = self.get_columns()
        kc_mavg_normalized, kc_upper_normalized, kc_lower_normalized = self.get_feature_columns()

        data_frame[kc_mavg_normalized] = (data_frame[kc_mavg] - data_frame["close"]) / data_frame["close"]
        data_frame[kc_upper_normalized] = (data_frame[kc_upper] - data_frame["close"]) / data_frame["close"]
        data_frame[kc_lower_normalized] = (data_frame[kc_lower] - data_frame["close"]) / data_frame["close"]

        return data_frame

    def get_feature_columns(self) -> List[str]:
        return [column + "_normalized" for column in self.get_columns()]
