import pytest
from quant_core.enums.time_period import TimePeriod
from quant_core.utils.chart_utils import check_df_sorted, get_data_frame_period
from quant_dev.builder import Builder
from sklearn.utils import shuffle


class TestChartUtilities:
    def test_is_monotonically_increasing(self) -> None:
        data_frame = Builder().get_random_chart_data_frame()

        check_df_sorted(data_frame)

    def test_is_not_monotonically_increasing(self) -> None:
        data_frame = Builder().get_random_chart_data_frame()

        data_frame = shuffle(data_frame)

        with pytest.raises(AssertionError):
            check_df_sorted(data_frame)

    @pytest.mark.parametrize(
        "file_name,expected_period",
        [
            ("appl_1440.csv", TimePeriod.DAY),
            ("btcusd_240.csv", TimePeriod.HOUR_4),
            ("eurusd_60.csv", TimePeriod.HOUR_1),
            ("usdjpy_15.csv", TimePeriod.MINUTE_15),
        ],
    )
    def test_time_period_is_valid(self, file_name: str, expected_period: TimePeriod) -> None:
        data_frame = Builder().get_random_chart_data_frame(file_name=file_name)

        time_period = get_data_frame_period(data_frame)

        assert time_period is expected_period
