from typing import List
import pandas as pd
import numpy as np

from quant_core.features.feature import DataFeature
from quant_core.utils.chart_utils import check_df_sorted, check_enough_rows


class DataFeatureNadarayaWatsonEnvelope(DataFeature):
    """Data Feature for the Nadaraya-Watson Envelope."""

    def __init__(self, bandwidth: float = 5.0, std_multiplier: float = 2.0):
        self._bandwidth = bandwidth
        self._std_multiplier = std_multiplier

    def get_columns(self) -> List[str]:
        return [
            f"nw_mean_{self._bandwidth}_{self._std_multiplier}",
            f"nw_upper_{self._bandwidth}_{self._std_multiplier}",
            f"nw_lower_{self._bandwidth}_{self._std_multiplier}",
        ]

    def add_feature(self, data_frame: pd.DataFrame) -> pd.DataFrame:
        nw_mean_col, nw_upper_col, nw_lower_col = self.get_columns()
        if all(col in data_frame.columns for col in (nw_mean_col, nw_upper_col, nw_lower_col)):
            return data_frame

        check_df_sorted(data_frame)
        check_enough_rows(data_frame)

        close = data_frame["close"]
        mean = self._nadaraya_watson_estimate(close, self._bandwidth)
        std = close.rolling(window=20, min_periods=5).std()

        data_frame[nw_mean_col] = mean
        data_frame[nw_upper_col] = mean + self._std_multiplier * std
        data_frame[nw_lower_col] = mean - self._std_multiplier * std

        return data_frame

    def normalize_feature(self, data_frame: pd.DataFrame) -> pd.DataFrame:
        nw_mavg, nw_upper, nw_lower = self.get_columns()
        nw_mavg_normalized, nw_upper_normalized, nw_lower_normalized = self.get_feature_columns()

        data_frame[nw_mavg_normalized] = (data_frame[nw_mavg] - data_frame["close"]) / data_frame["close"]
        data_frame[nw_upper_normalized] = (data_frame[nw_upper] - data_frame["close"]) / data_frame["close"]
        data_frame[nw_lower_normalized] = (data_frame[nw_lower] - data_frame["close"]) / data_frame["close"]

        return data_frame

    def get_feature_columns(self) -> List[str]:
        return [col + "_normalized" for col in self.get_columns()]

    def _nadaraya_watson_estimate(self, prices: pd.Series, bandwidth: float) -> pd.Series:
        """Computes Nadaraya-Watson kernel regression with Gaussian kernel."""
        smoothed = np.full_like(prices, np.nan, dtype=np.float64)
        for i in range(len(prices)):
            window = prices[max(0, i - 50):i + 1]
            if len(window) < 2:
                continue
            weights = np.exp(-((np.arange(len(window)) - len(window) + 1) ** 2) / (2 * bandwidth ** 2))
            weights /= weights.sum()
            smoothed[i] = np.sum(window.values * weights)
        return pd.Series(smoothed, index=prices.index)
