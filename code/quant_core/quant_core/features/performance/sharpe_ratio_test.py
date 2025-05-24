import pytest

from quant_core.chart.features.performance.sharpe_ratio import DataFeatureSharpeRatio
from quant_core.enums.trade_direction import TradeDirection
from quant_dev.builder import Builder


class TestDataFeatureSharpeRatio:
    def test_multiple_columns_with_different_parameters(self) -> None:
        data_frame = Builder().get_random_chart_data_frame()
        directions = [TradeDirection.LONG, TradeDirection.SHORT]
        free_percents = Builder().get_random_items(list(range(1, 100)), 2)
        bars = Builder().get_random_items(list(range(1, 100)), 2)

        features = [
            DataFeatureSharpeRatio(direction=direction, annual_risk_free_percent=free_percent, rolling_window_bars=bars)
            for direction, free_percent, bars in zip(directions, free_percents, bars)
        ]

        for feature in features:
            data_frame = feature.add_feature(data_frame)

        assert all(column in data_frame.columns for feature in features for column in feature.get_columns())

    @pytest.mark.parametrize(
        "file_name,direction,annual_risk_free_percentage,bars,expected_values",
        [
            (
                "appl_1440.csv",
                TradeDirection.LONG,
                2.0,
                60,
                [
                    -0.5013,
                    -0.4479,
                    -0.4175,
                    -0.4069,
                    -0.4722,
                    -0.4240,
                    -0.4169,
                    -0.4768,
                    -0.5270,
                    -0.4966,
                    -0.4269,
                    -0.3831,
                    -0.3645,
                    -0.2882,
                    -0.3332,
                    -0.3301,
                    -0.3270,
                    -0.3250,
                    -0.3221,
                    -0.3341,
                ],
            ),
            (
                "btcusd_240.csv",
                TradeDirection.SHORT,
                3.0,
                100,
                [
                    -0.2736,
                    -0.3069,
                    -0.2944,
                    -0.2656,
                    -0.2499,
                    -0.2462,
                    -0.2575,
                    -0.2738,
                    -0.2916,
                    -0.2849,
                    -0.3247,
                    -0.3165,
                    -0.3376,
                    -0.3289,
                    -0.2906,
                    -0.1863,
                    -0.2170,
                    -0.2077,
                    -0.2309,
                    -0.2460,
                ],
            ),
        ],
    )
    def test_correct_calculation(
        self,
        file_name: str,
        direction: TradeDirection,
        annual_risk_free_percentage: float,
        bars: int,
        expected_values: list[float],
    ) -> None:
        """Compare with manually calculated values for Returns."""
        feature = DataFeatureSharpeRatio(
            direction=direction, annual_risk_free_percent=annual_risk_free_percentage, rolling_window_bars=bars
        )
        data_frame = Builder().get_random_chart_data_frame(file_name=file_name)
        column_name = feature.get_columns()[0]
        feature_column_name = feature.get_feature_columns()[0]

        data_frame = feature.add_feature(data_frame)
        data_frame = feature.normalize_feature(data_frame)

        assert column_name == feature_column_name
        assert (
            data_frame[column_name].apply(lambda x: round(x, 4))[-len(expected_values) :].values.tolist()
            == expected_values
        )
