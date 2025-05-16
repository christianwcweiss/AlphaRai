import pandas as pd
import pytest

from quant_core.metrics.trade_metric_over_time import TradeMetricOverTime
from quant_dev.builder import Builder


class TestTradeMetricOverTime:

    @pytest.mark.parametrize("group_by_account_id,group_by_symbol", [(True, False), (False, True), (True, True)])
    def test_groups(self, group_by_account_id: bool, group_by_symbol: bool) -> None:
        trade_metric_over_time = TradeMetricOverTime

        groups = trade_metric_over_time._get_groups(
            group_by_account_id=group_by_account_id, group_by_symbol=group_by_symbol
        )

        assert isinstance(groups, list)
        if group_by_account_id:
            assert "account_id" in groups
        if group_by_symbol:
            assert "symbol" in groups

        if not group_by_account_id and not group_by_symbol:
            assert len(groups) == 0

        if group_by_account_id and group_by_symbol:
            assert len(groups) == 2

    def test_normalize_time(self) -> None:
        trade_metric_over_time = TradeMetricOverTime
        data_frame = Builder.get_trade_history()

        normalized_df = trade_metric_over_time._normalize_time(data_frame)

        assert "time" in normalized_df.columns
        assert len(normalized_df) == len(data_frame)
        assert normalized_df["time"].is_monotonic_increasing
        assert normalized_df["time"].dtype == "datetime64[ns]"

    @pytest.mark.parametrize("skip_head", [True, False])
    def test_rolling_window_days(self, skip_head: bool) -> None:
        trade_metric_over_time = TradeMetricOverTime
        data_frame = Builder.get_trade_history()
        data_frame = trade_metric_over_time._normalize_time(data_frame=data_frame)
        rolling_window = Builder.build_random_int(10, 50)
        min_date = data_frame["time"].min().replace(hour=0, minute=0, second=0, microsecond=0)
        max_date = data_frame["time"].max().replace(hour=0, minute=0, second=0, microsecond=0)

        rolling_windows = trade_metric_over_time.get_rolling_windows(
            data_frame, rolling_window=rolling_window, skip_head=skip_head
        )

        assert isinstance(rolling_windows, dict)
        assert max_date in rolling_windows.keys()
        if skip_head:
            assert len(rolling_windows) == len(pd.date_range(min_date, max_date, freq="D")) - rolling_window
        else:
            assert len(rolling_windows) == len(pd.date_range(min_date, max_date, freq="D"))

        for window_time, window_df in rolling_windows.items():
            if window_time is pd.NaT or window_df.empty:
                continue

            assert isinstance(window_time, pd.Timestamp)
            assert isinstance(window_df, pd.DataFrame)
            assert "time" in window_df.columns
            assert len(window_df) >= 0
            assert window_df["time"].is_monotonic_increasing
            assert window_df["time"].dtype == "datetime64[ns]"
            assert window_df["agg_time"].min() >= window_time - pd.Timedelta(days=rolling_window)
            assert window_df["agg_time"].max() <= window_time

        if not skip_head:
            concatenate_df = pd.concat(rolling_windows.values()).drop_duplicates()
            assert len(concatenate_df) == len(
                data_frame
            ), f"Missing:{data_frame[~data_frame['time'].isin(concatenate_df['time'])]}"

    @pytest.mark.parametrize("skip_head", [True, False])
    def test_rolling_window_hours(self, skip_head: bool) -> None:
        trade_metric_over_time = TradeMetricOverTime
        data_frame = Builder.get_trade_history()
        data_frame = trade_metric_over_time._normalize_time(data_frame=data_frame)
        rolling_window = Builder.build_random_int(10, 50)
        min_date = data_frame["time"].min().replace(minute=0, second=0, microsecond=0)
        max_date = data_frame["time"].max().replace(minute=0, second=0, microsecond=0)

        rolling_windows = trade_metric_over_time.get_rolling_windows(
            data_frame, rolling_window=rolling_window, skip_head=skip_head, aggregation_resolution="H"
        )

        assert isinstance(rolling_windows, dict)
        if skip_head:
            assert len(rolling_windows) == len(pd.date_range(min_date, max_date, freq="H")) - rolling_window
        else:
            assert len(rolling_windows) == len(pd.date_range(min_date, max_date, freq="H"))

        for window_time, window_df in rolling_windows.items():
            if window_time is pd.NaT or window_df.empty:
                continue

            assert isinstance(window_time, pd.Timestamp)
            assert isinstance(window_df, pd.DataFrame)
            assert "time" in window_df.columns
            assert len(window_df) >= 0
            assert window_df["time"].is_monotonic_increasing
            assert window_df["time"].dtype == "datetime64[ns]"
            assert window_df["agg_time"].min() >= window_time - pd.Timedelta(hours=rolling_window)
            assert window_df["agg_time"].max() <= window_time
            assert window_df["time"].dt.floor("H").min() >= window_time - pd.Timedelta(hours=rolling_window)
            assert window_df["time"].dt.floor("H").max() <= window_time

        if not skip_head:
            concatenate_df = pd.concat(rolling_windows.values()).drop_duplicates()
            assert len(concatenate_df) == len(
                data_frame
            ), f"Missing:{data_frame[~data_frame['time'].isin(concatenate_df['time'])]}"

    def test_unknown_aggregation_resolution(self) -> None:
        trade_metric_over_time = TradeMetricOverTime
        data_frame = Builder.get_trade_history()

        with pytest.raises(ValueError, match="Unsupported aggregation resolution: unknown"):
            trade_metric_over_time.get_rolling_windows(
                data_frame=data_frame,
                rolling_window=30,
                skip_head=False,
                aggregation_resolution="unknown",
            )
