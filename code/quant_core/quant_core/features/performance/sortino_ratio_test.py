import pytest

from quant_core.chart.features.performance.sortino_ratio import DataFeatureSortinoRatio
from quant_core.enums.trade_direction import TradeDirection
from quant_dev.builder import Builder


class TestDataFeatureSortinoRatio:
    def test_multiple_columns_with_different_parameters(self) -> None:
        data_frame = Builder().get_random_chart_data_frame()
        directions = [TradeDirection.LONG, TradeDirection.SHORT]
        free_percents = Builder().get_random_items(list(range(1, 100)), 2)
        bars = Builder().get_random_items(list(range(1, 100)), 2)

        features = [
            DataFeatureSortinoRatio(
                direction=direction, annual_risk_free_percent=free_percent, rolling_window_bars=bars
            )
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
                    -0.6816,
                    -0.5922,
                    -0.5499,
                    -0.5327,
                    -0.6027,
                    -0.5496,
                    -0.5356,
                    -0.602,
                    -0.6789,
                    -0.6209,
                    -0.5434,
                    -0.4931,
                    -0.4724,
                    -0.365,
                    -0.4227,
                    -0.4187,
                    -0.4149,
                    -0.4114,
                    -0.4078,
                    -0.4218,
                ],
            ),
            (
                "btcusd_240.csv",
                TradeDirection.SHORT,
                3.0,
                100,
                [
                    -0.368,
                    -0.4107,
                    -0.3913,
                    -0.3507,
                    -0.3288,
                    -0.3235,
                    -0.3396,
                    -0.3641,
                    -0.3871,
                    -0.3772,
                    -0.4303,
                    -0.418,
                    -0.4483,
                    -0.4353,
                    -0.3862,
                    -0.2496,
                    -0.2946,
                    -0.2822,
                    -0.3157,
                    -0.3392,
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
        feature = DataFeatureSortinoRatio(
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
