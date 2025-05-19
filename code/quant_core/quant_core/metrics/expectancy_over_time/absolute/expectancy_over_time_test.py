import numpy as np
import pandas as pd
import pytest

from quant_core.metrics.expectancy_over_time.absolute.expectancy_over_time import ExpectancyOverTimeAbsolute
from quant_core.metrics.trade_metric_over_time import TradeMetricOverTime
from quant_dev.builder import Builder


class TestExpectancyOverTimeAbsolute:
    @pytest.mark.parametrize(
        "group_by_account_id,group_by_symbol",
        [
            (True, False),
            (False, True),
            (True, True),
        ],
    )
    def test_columns_in_data_frame(
        self,
        group_by_account_id: bool,
        group_by_symbol: bool,
    ) -> None:
        data_frame = Builder.get_trade_history()

        expectancy_df = ExpectancyOverTimeAbsolute().calculate(
            data_frame,
            group_by_account_id=group_by_account_id,
            group_by_symbol=group_by_symbol,
            rolling_window=30,
        )

        assert "expectancy" in expectancy_df.columns

        if group_by_account_id:
            assert "account_id" in expectancy_df.columns

        if group_by_symbol:
            assert "symbol" in expectancy_df.columns

    @pytest.mark.parametrize("expected_result", [0.41])
    def test_ungrouped_result(self, expected_result: float) -> None:
        data_frame = Builder.get_trade_history()

        expectancy_df = ExpectancyOverTimeAbsolute().calculate(
            data_frame, group_by_account_id=False, group_by_symbol=False, rolling_window=30
        )

        assert "account_id" not in expectancy_df.columns
        assert "symbol" not in expectancy_df.columns
        assert round(expectancy_df["expectancy"].iloc[-1], 2) == expected_result

    def test_grouped_by_account_result(self) -> None:
        data_frame = Builder.get_trade_history()
        # Verified manual calculation
        account_results = {
            "A2NRRYL4": 1.36,
            "0EUEV5SO": -0.64,
        }

        expectancy_df = ExpectancyOverTimeAbsolute().calculate(
            data_frame, group_by_account_id=True, group_by_symbol=False
        )

        assert "account_id" in expectancy_df.columns
        assert "symbol" not in expectancy_df.columns
        assert "expectancy" in expectancy_df.columns

        for account_id in expectancy_df["account_id"].unique():
            account_expectancy_df = expectancy_df[expectancy_df["account_id"] == account_id]
            assert len(account_expectancy_df) > 0
            assert round(account_expectancy_df.iloc[-1]["expectancy"], 2) == account_results[account_id]

    def test_grouped_by_symbol_result(self) -> None:
        data_frame = Builder.get_trade_history()
        # Verified manual calculation
        symbol_results = {
            "EURUSD": 9.48,
            "GBPUSD": 3.78,
            "USDCHF": -2.35,
            "USDJPY": -3.88,
        }

        expectancy_df = ExpectancyOverTimeAbsolute().calculate(
            data_frame, group_by_account_id=False, group_by_symbol=True
        )

        assert "account_id" not in expectancy_df.columns
        assert "symbol" in expectancy_df.columns
        assert "expectancy" in expectancy_df.columns

        for symbol in expectancy_df["symbol"].unique():
            if symbol is np.nan:
                continue

            symbol_expectancy_df = expectancy_df[expectancy_df["symbol"] == symbol]
            assert len(symbol_expectancy_df) > 0
            assert round(symbol_expectancy_df.iloc[-1]["expectancy"], 2) == symbol_results[symbol]

    def test_grouped_by_account_and_symbol_result(self) -> None:
        data_frame = Builder.get_trade_history()
        # Verified manual calculation
        account_symbol_results = {
            "A2NRRYL4": {
                "EURUSD": 18.11,
                "GBPUSD": 5.39,
                "USDCHF": -3.15,
                "USDJPY": -7.13,
            },
            "0EUEV5SO": {
                "EURUSD": -2.74,
                "GBPUSD": 1.73,
                "USDCHF": -1.48,
                "USDJPY": -1.12,
            },
        }

        expectancy_df = ExpectancyOverTimeAbsolute().calculate(
            data_frame, group_by_account_id=True, group_by_symbol=True
        )

        assert "account_id" in expectancy_df.columns
        assert "symbol" in expectancy_df.columns
        assert "expectancy" in expectancy_df.columns

        for account_id in expectancy_df["account_id"].unique():
            for symbol in expectancy_df[expectancy_df["account_id"] == account_id]["symbol"].unique():
                if symbol is np.nan:
                    continue

                account_symbol_expectancy_df = expectancy_df[
                    (expectancy_df["account_id"] == account_id) & (expectancy_df["symbol"] == symbol)
                ]
                assert len(account_symbol_expectancy_df) > 0
                assert (
                    round(account_symbol_expectancy_df.iloc[-1]["expectancy"], 2)
                    == account_symbol_results[account_id][symbol]
                ), (
                    f"Expected {account_symbol_results[account_id][symbol]} "
                    f"for account {account_id} and symbol {symbol}, "
                    f"but got {round(account_symbol_expectancy_df.iloc[-1]['expectancy'], 2)}"
                )

    @pytest.mark.parametrize("expected_result", [0.18])
    def test_ungrouped_result(self, expected_result: float) -> None:
        data_frame = Builder.get_trade_history()
        rolling_window = Builder.build_random_int(10, 50)
        data_frame = ExpectancyOverTimeAbsolute()._normalize_time(data_frame)
        min_date = data_frame["opened_at"].min().replace(hour=0, minute=0, second=0, microsecond=0)
        max_date = data_frame["closed_at"].max().replace(hour=0, minute=0, second=0, microsecond=0)

        expectancy_df = ExpectancyOverTimeAbsolute().calculate(
            data_frame, group_by_account_id=False, group_by_symbol=False, rolling_window=rolling_window
        )

        assert expectancy_df["time"].is_monotonic_increasing
        assert "account_id" not in expectancy_df.columns
        assert "symbol" not in expectancy_df.columns
        assert "expectancy" in expectancy_df.columns
        assert len(expectancy_df) == len(pd.date_range(min_date, max_date)) - rolling_window
        assert round(expectancy_df["expectancy"].iloc[-1], 2) == expected_result
