from typing import List

import pandas as pd

from quant_core.chart.feature import DataFeature
from quant_core.utils.chart_utils import check_df_sorted, check_enough_rows


class DataFeatureHeikinAshi(DataFeature):

    def get_columns(self) -> List[str]:
        return ["ha_open", "ha_close", "ha_high", "ha_low"]

    def add_feature(self, data_frame: pd.DataFrame) -> pd.DataFrame:
        ha_open_column, ha_close_column, ha_high_column, ha_low_column = self.get_columns()
        if all(column in data_frame for column in self.get_columns()):
            return data_frame

        check_df_sorted(data_frame=data_frame)
        check_enough_rows(data_frame=data_frame)

        data_frame[ha_open_column] = (data_frame["open"].shift(1) + data_frame["close"].shift(1)) / 2
        data_frame[ha_close_column] = (
            data_frame["open"] + data_frame["high"] + data_frame["low"] + data_frame["close"]
        ) / 4
        data_frame[ha_high_column] = data_frame[["high", ha_open_column, ha_close_column]].max(axis=1)
        data_frame[ha_low_column] = data_frame[["low", ha_open_column, ha_close_column]].min(axis=1)

        return data_frame

    def normalize_feature(self, data_frame: pd.DataFrame) -> pd.DataFrame:
        ha_open_column, ha_close_column, ha_high_column, ha_low_column = self.get_columns()
        ha_normalized_open_column, ha_normalized_close_column, ha_normalized_high_column, ha_normalized_low_column = (
            self.get_feature_columns()
        )

        data_frame[ha_normalized_open_column] = (data_frame[ha_open_column] - data_frame["open"]) / data_frame["open"]
        data_frame[ha_normalized_close_column] = (data_frame[ha_close_column] - data_frame["close"]) / data_frame[
            "close"
        ]
        data_frame[ha_normalized_high_column] = (data_frame[ha_high_column] - data_frame["high"]) / data_frame["high"]
        data_frame[ha_normalized_low_column] = (data_frame[ha_low_column] - data_frame["low"]) / data_frame["low"]

        return data_frame

    def get_feature_columns(self) -> List[str]:
        return [column + "_normalized" for column in self.get_columns()]
