from typing import List

import pytest
from quant_core.chart.features.performance.draw_down_up import DataFeatureDrawDownAndUp
from quant_core.enums.trade_direction import TradeDirection
from quant_dev.builder import Builder


class TestDataFeatureDrawDownAndUp:
    def test_multiple_columns_with_different_parameters(self) -> None:
        data_frame = Builder().get_random_chart_data_frame()
        directions = [TradeDirection.LONG, TradeDirection.SHORT]
        horizons = Builder().get_random_items(list(range(1, 100)), 2)

        features = [
            DataFeatureDrawDownAndUp(direction=direction, horizon=horizon)
            for direction, horizon in zip(directions, horizons)
        ]

        for feature in features:
            data_frame = feature.add_feature(data_frame)

        assert all(column in data_frame.columns for feature in features for column in feature.get_columns())

    @pytest.mark.parametrize(
        "file_name,direction,horizon,expected_draw_down_values,expected_draw_up_values,"
        "expected_draw_down_feature_values,expected_draw_up_feature_values",
        [
            (
                "appl_1440.csv",
                TradeDirection.LONG,
                5,
                [
                    -18.861,
                    -19.561,
                    -16.141,
                    -14.381,
                    -4.001,
                    -7.021,
                    -6.700,
                    -7.431,
                    -1.941,
                    -1.911,
                    -5.970,
                    -9.650,
                    -14.289,
                    -17.730,
                    -17.190,
                    -16.649,
                    -15.230,
                    -9.990,
                    -6.219,
                    -7.711,
                ],
                [
                    1.930,
                    0.830,
                    3.220,
                    11.360,
                    19.210,
                    14.420,
                    14.741,
                    14.010,
                    19.500,
                    6.350,
                    2.610,
                    0.079,
                    0.860,
                    0.400,
                    0.940,
                    1.170,
                    0.879,
                    3.110,
                    1.621,
                    0.390,
                ],
                [
                    -0.0792,
                    -0.0817,
                    -0.0680,
                    -0.0610,
                    -0.0176,
                    -0.0302,
                    -0.0288,
                    -0.0319,
                    -0.0085,
                    -0.0084,
                    -0.0257,
                    -0.0407,
                    -0.0592,
                    -0.0724,
                    -0.0703,
                    -0.0680,
                    -0.0619,
                    -0.0407,
                    -0.0252,
                    -0.0309,
                ],
                [
                    0.0081,
                    0.0035,
                    0.0136,
                    0.0482,
                    0.0843,
                    0.0620,
                    0.0634,
                    0.0601,
                    0.0857,
                    0.0279,
                    0.0112,
                    0.0003,
                    0.0036,
                    0.0016,
                    0.0038,
                    0.0048,
                    0.0036,
                    0.0127,
                    0.0066,
                    0.0016,
                ],
            )
        ],
    )
    def test_correct_calculation(
        self,
        file_name: str,
        direction: TradeDirection,
        horizon: int,
        expected_draw_down_values: List[float],
        expected_draw_up_values: List[float],
        expected_draw_down_feature_values: List[float],
        expected_draw_up_feature_values: List[float],
    ) -> None:
        """Compare with manually calculated values for DrawDowns/Ups."""
        feature = DataFeatureDrawDownAndUp(direction=direction, horizon=horizon)
        data_frame = Builder().get_random_chart_data_frame(file_name=file_name)

        draw_down_column_name, draw_up_column_name = feature.get_columns()
        draw_down_feature_column_name, draw_up_feature_column_name = feature.get_feature_columns()

        data_frame = feature.add_feature(data_frame)
        data_frame = feature.normalize_feature(data_frame)

        assert (
            data_frame[draw_down_column_name]
            .apply(lambda x: round(x, 4))[-len(expected_draw_down_values) :]
            .values.tolist()
            == expected_draw_down_values
        )
        assert (
            data_frame[draw_up_column_name]
            .apply(lambda x: round(x, 4))[-len(expected_draw_up_values) :]
            .values.tolist()
            == expected_draw_up_values
        )
        assert (
            data_frame[draw_down_feature_column_name]
            .apply(lambda x: round(x, 4))[-len(expected_draw_down_feature_values) :]
            .values.tolist()
            == expected_draw_down_feature_values
        )
        assert (
            data_frame[draw_up_feature_column_name]
            .apply(lambda x: round(x, 4))[-len(expected_draw_up_feature_values) :]
            .values.tolist()
            == expected_draw_up_feature_values
        )
