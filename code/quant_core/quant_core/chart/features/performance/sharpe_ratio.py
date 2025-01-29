from typing import List

import numpy as np
import pandas as pd

from quant_core.chart.feature import DataFeature
from quant_core.chart.features.performance.returns import DataFeatureReturns
from quant_core.enums.trade_direction import TradeDirection
from quant_core.utils.chart_utils import check_df_sorted, check_enough_rows, get_data_frame_period


class DataFeatureSharpeRatio(DataFeature):
    def __init__(
        self,
        direction: TradeDirection,
        annual_risk_free_percent: float = 2.0,
        rolling_window_bars: int = 60,
    ) -> None:
        self._direction = direction.normalize()
        self._annual_risk_free_percent = annual_risk_free_percent / 100.0
        self._rolling_window_bars = rolling_window_bars

    def get_columns(self) -> List[str]:
        return [
            f"sharpe_ratio_{self._rolling_window_bars}_{round(self._annual_risk_free_percent, 2)}_{self._direction.value.lower()}"
        ]

    def add_feature(self, data_frame: pd.DataFrame) -> pd.DataFrame:
        sharpe_column = self.get_columns()[0]
        if sharpe_column in data_frame:
            return data_frame

        check_df_sorted(data_frame=data_frame)
        check_enough_rows(data_frame=data_frame)

        time_period = get_data_frame_period(data_frame)

        return_feature = DataFeatureReturns(direction=self._direction, horizon=1)
        data_frame = return_feature.add_feature(data_frame)
        return_column = return_feature.get_columns()[0]

        data_frame[sharpe_column] = np.nan
        for i in range(self._rolling_window_bars - 1, len(data_frame)):
            start_idx = i - (self._rolling_window_bars - 1)
            window_rets = data_frame[return_column].iloc[start_idx : i + 1].dropna()
            if len(window_rets) < 2:
                continue

            mean_return = window_rets.mean()
            std_return = window_rets.std()

            if std_return == 0 or np.isnan(std_return):
                sharpe_val = np.nan
            else:
                total_minutes = len(window_rets) * time_period.value
                fractional_years = total_minutes / (60 * 24 * 365)
                annual_factor = 1.0 / fractional_years if fractional_years != 0 else np.nan
                annual_mean = mean_return * annual_factor
                annual_std = std_return * np.sqrt(annual_factor)
                sharpe_val = (annual_mean - self._annual_risk_free_percent) / annual_std

            data_frame.at[data_frame.index[i], sharpe_column] = sharpe_val

        data_frame.loc[data_frame.index[: self._rolling_window_bars - 1], sharpe_column] = np.nan

        return data_frame

    def normalize_feature(self, data_frame: pd.DataFrame) -> pd.DataFrame:
        return data_frame

    def get_feature_columns(self) -> List[str]:
        return self.get_columns()
