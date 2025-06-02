from typing import List

import pytest
from quant_core.chart.features.performance.returns import DataFeatureReturns
from quant_core.enums.trade_direction import TradeDirection
from quant_dev.builder import Builder


class TestDataFeatureReturns:
    def test_multiple_columns_with_different_parameters(self) -> None:
        data_frame = Builder().get_random_chart_data_frame()
        directions = [TradeDirection.LONG, TradeDirection.SHORT]
        horizons = Builder().get_random_items(list(range(1, 100)), 2)

        features = [
            DataFeatureReturns(direction=direction, horizon=horizon) for direction, horizon in zip(directions, horizons)
        ]

        for feature in features:
            data_frame = feature.add_feature(data_frame)

        assert all(column in data_frame.columns for feature in features for column in feature.get_columns())

    @pytest.mark.parametrize(
        "file_name,direction,horizon,expected_values",
        [
            (
                "appl_1440.csv",
                TradeDirection.LONG,
                1,
                [
                    0.0369,
                    0.0046,
                    -0.0075,
                    -0.0074,
                    -0.0333,
                    0.0210,
                    -0.0014,
                    0.0031,
                    -0.0235,
                    -0.0001,
                    0.0220,
                    0.0181,
                    0.0196,
                    0.0143,
                    -0.0022,
                    0.0017,
                    0.0044,
                    -0.0012,
                    0.0066,
                    0.0095,
                ],
            ),
            (
                "btcusd_240.csv",
                TradeDirection.SHORT,
                5,
                [
                    -0.0112,
                    -0.0080,
                    0.0013,
                    0.0048,
                    0.0080,
                    0.0032,
                    -0.0079,
                    -0.0117,
                    -0.0121,
                    -0.0104,
                    -0.0069,
                    -0.0024,
                    -0.0073,
                    -0.0098,
                    0.0033,
                    0.0241,
                    0.0188,
                    0.0302,
                    0.0205,
                    0.0066,
                ],
            ),
        ],
    )
    def test_correct_calculation(
        self, file_name: str, direction: TradeDirection, horizon: int, expected_values: List[float]
    ) -> None:
        """Compare with manually calculated values for Returns."""
        feature = DataFeatureReturns(direction=direction, horizon=horizon)
        data_frame = Builder().get_random_chart_data_frame(file_name=file_name)

        column_name = feature.get_columns()[0]
        feature_column_name = feature.get_feature_columns()[0]
        data_frame = feature.add_feature(data_frame)
        data_frame = feature.normalize_feature(data_frame)

        assert (
            data_frame[column_name].apply(lambda x: round(x, 4))[-len(expected_values) :].values.tolist()
            == expected_values
        )
        assert (
            data_frame[feature_column_name].apply(lambda x: round(x, 4))[-len(expected_values) :].values.tolist()
            == expected_values
        )
