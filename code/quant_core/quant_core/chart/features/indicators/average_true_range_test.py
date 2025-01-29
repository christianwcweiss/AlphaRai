from typing import List

import pytest

from quant_core.chart.features.indicators.average_true_range import DataFeatureAverageTrueRange
from quant_dev.builder import Builder


class TestDataFeatureAverageTrueRange:
    def test_multiple_columns_with_different_parameters(self) -> None:
        data_frame = Builder().get_random_chart_data_frame()
        atr_periods = Builder().get_random_items(list(range(1, 100)), 5)
        features = [DataFeatureAverageTrueRange(atr_period=atr_period) for atr_period in atr_periods]

        for feature in features:
            data_frame = feature.add_feature(data_frame)

        assert all(column in data_frame.columns for feature in features for column in feature.get_columns())

    @pytest.mark.parametrize(
        "file_name,period,expected_values,expected_normalized_values",
        [
            (
                "appl_1440.csv",
                14,
                [
                    5.82,
                    5.82,
                    5.66,
                    6.24,
                    6.51,
                    6.51,
                    6.36,
                    6.15,
                    6.18,
                    5.98,
                    6.10,
                    6.11,
                    6.16,
                    6.03,
                    5.84,
                    5.62,
                    5.39,
                    5.26,
                    5.19,
                    5.18,
                ],
                [
                    0.0244,
                    0.0243,
                    0.0238,
                    0.0264,
                    0.0286,
                    0.0280,
                    0.0274,
                    0.0264,
                    0.0272,
                    0.0263,
                    0.0262,
                    0.0258,
                    0.0255,
                    0.0246,
                    0.0239,
                    0.0230,
                    0.0219,
                    0.0214,
                    0.0210,
                    0.0208,
                ],
            ),
            (
                "btcusd_240.csv",
                10,
                [
                    1024.30,
                    986.76,
                    975.18,
                    944.49,
                    1033.19,
                    1100.60,
                    1066.98,
                    1008.00,
                    1049.02,
                    1023.09,
                    959.26,
                    928.27,
                    919.18,
                    870.95,
                    933.81,
                    1065.18,
                    1105.09,
                    1097.17,
                    1276.95,
                    1186.93,
                ],
                [
                    0.0105,
                    0.0102,
                    0.0101,
                    0.0098,
                    0.0107,
                    0.0114,
                    0.0110,
                    0.0103,
                    0.0108,
                    0.0105,
                    0.0098,
                    0.0095,
                    0.0093,
                    0.0089,
                    0.0096,
                    0.0112,
                    0.0115,
                    0.0115,
                    0.0133,
                    0.0123,
                ],
            ),
        ],
    )
    def test_correct_calculation(
        self, file_name: str, period: int, expected_values: List[float], expected_normalized_values: List[float]
    ) -> None:
        """Compare with manually calculated values for ATR."""
        feature = DataFeatureAverageTrueRange(atr_period=period)
        data_frame = Builder().get_random_chart_data_frame(file_name=file_name)

        column_name = feature.get_columns()[0]
        feature_column_name = feature.get_feature_columns()[0]
        data_frame = feature.add_feature(data_frame)
        data_frame = feature.normalize_feature(data_frame)

        assert (
            data_frame[column_name].apply(lambda x: round(x, 2))[-len(expected_values) :].values.tolist()
            == expected_values
        )
        assert (
            data_frame[feature_column_name]
            .apply(lambda x: round(x, 4))[-len(expected_normalized_values) :]
            .values.tolist()
            == expected_normalized_values
        )
