import numpy as np
import pandas as pd
import pytest

from quant_core.metrics.expectancy_over_time.expectancy_over_time import ExpectancyOverTime
from quant_dev.builder import Builder


class TestExpectancyOverTimeAbsolute:
    @pytest.mark.parametrize(
        "group_by_account_id,group_by_symbol",
        [
            (False, False),
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

        expectancy_df = ExpectancyOverTime().calculate(
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

        expectancy_df = ExpectancyOverTime().calculate(
            data_frame, group_by_account_id=False, group_by_symbol=False, rolling_window=30
        )

        assert "account_id" not in expectancy_df.columns
        assert "symbol" not in expectancy_df.columns
        assert round(expectancy_df["expectancy"].iloc[-1], 2) == expected_result

    def test_grouped_by_account_result(self) -> None:
        data_frame = Builder.get_trade_history()
        # Verified manual calculation
        account_results_absolute = {
            "A2NRRYL4": 2.02,
            "0EUEV5SO": -0.61,
        }
        account_results_relative = {
            "A2NRRYL4": 3e-05,
            "0EUEV5SO": -6e-05,
        }

        expectancy_df = ExpectancyOverTime().calculate(data_frame, group_by_account_id=True, group_by_symbol=False)

        assert "account_id" in expectancy_df.columns
        assert "symbol" not in expectancy_df.columns
        assert "expectancy" in expectancy_df.columns
        assert "expectancy_pct" in expectancy_df.columns

        for account_id in expectancy_df["account_id"].unique():
            account_expectancy_df = expectancy_df[expectancy_df["account_id"] == account_id]
            assert len(account_expectancy_df) > 0
            assert round(account_expectancy_df.iloc[-1]["expectancy"], 2) == account_results_absolute[account_id]
            assert round(account_expectancy_df.iloc[-1]["expectancy_pct"], 5) == account_results_relative[account_id]

    def test_grouped_by_symbol_result(self) -> None:
        data_frame = Builder.get_trade_history()
        # Verified manual calculation
        symbol_results_absolute = {
            "EURUSD": 9.48,
            "GBPUSD": 3.78,
            "USDCHF": -2.98,
            "USDJPY": -0.64,
        }
        symbol_results_relative = {
            "EURUSD": 0.00095,
            "GBPUSD": 5e-05,
            "USDCHF": -0.0003,
            "USDJPY": -1e-05,
        }

        expectancy_df = ExpectancyOverTime().calculate(data_frame, group_by_account_id=False, group_by_symbol=True)

        assert "account_id" not in expectancy_df.columns
        assert "symbol" in expectancy_df.columns
        assert "expectancy" in expectancy_df.columns
        assert "expectancy_pct" in expectancy_df.columns

        for symbol in expectancy_df["symbol"].unique():
            if symbol is np.nan:
                continue

            symbol_expectancy_df = expectancy_df[expectancy_df["symbol"] == symbol]
            assert len(symbol_expectancy_df) > 0
            assert round(symbol_expectancy_df.iloc[-1]["expectancy"], 2) == symbol_results_absolute[symbol]
            assert round(symbol_expectancy_df.iloc[-1]["expectancy_pct"], 5) == symbol_results_relative[symbol]

    def test_grouped_by_account_and_symbol_result(self) -> None:
        data_frame = Builder.get_trade_history()
        # Verified manual calculation
        account_symbol_results_absolute = {
            "A2NRRYL4": {
                "EURUSD": 18.11,
                "GBPUSD": 5.39,
                "USDCHF": -4.09,
                "USDJPY": -1.08,
            },
            "0EUEV5SO": {
                "EURUSD": -2.74,
                "GBPUSD": 1.73,
                "USDCHF": -1.78,
                "USDJPY": -0.28,
            },
        }
        account_symbol_results_relative = {
            "A2NRRYL4": {
                "EURUSD": 0.00023,
                "GBPUSD": 7e-05,
                "USDCHF": -5e-05,
                "USDJPY": -1e-05,
            },
            "0EUEV5SO": {
                "EURUSD": -0.00027,
                "GBPUSD": 0.00017,
                "USDCHF": -0.00018,
                "USDJPY": -3e-05,
            },
        }

        expectancy_df = ExpectancyOverTime().calculate(data_frame, group_by_account_id=True, group_by_symbol=True)

        assert "account_id" in expectancy_df.columns
        assert "symbol" in expectancy_df.columns
        assert "expectancy" in expectancy_df.columns
        assert "expectancy_pct" in expectancy_df.columns

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
                    == account_symbol_results_absolute[account_id][symbol]
                ), (
                    f"Expected {account_symbol_results_absolute[account_id][symbol]} "
                    f"for account {account_id} and symbol {symbol}, "
                    f"but got {round(account_symbol_expectancy_df.iloc[-1]['expectancy'], 2)}"
                )
                assert (
                    round(account_symbol_expectancy_df.iloc[-1]["expectancy_pct"], 5)
                    == account_symbol_results_relative[account_id][symbol]
                ), (
                    f"Expected {account_symbol_results_relative[account_id][symbol]} "
                    f"for account {account_id} and symbol {symbol}, "
                    f"but got {round(account_symbol_expectancy_df.iloc[-1]['expectancy_pct'], 5)}"
                )

    @pytest.mark.parametrize("expected_result_absolute,expected_result_relative", [(0.77, 1e-05)])
    def test_ungrouped_result(self, expected_result_absolute: float, expected_result_relative: float) -> None:
        data_frame = Builder.get_trade_history()
        data_frame = ExpectancyOverTime()._normalize_time(data_frame)
        min_date = data_frame["opened_at"].min().replace(hour=0, minute=0, second=0, microsecond=0)
        max_date = data_frame["closed_at"].max().replace(hour=0, minute=0, second=0, microsecond=0)

        expectancy_df = ExpectancyOverTime().calculate(
            data_frame, group_by_account_id=False, group_by_symbol=False, rolling_window=30
        )

        assert expectancy_df["time"].is_monotonic_increasing
        assert "account_id" not in expectancy_df.columns
        assert "symbol" not in expectancy_df.columns
        assert "expectancy" in expectancy_df.columns
        assert "expectancy_pct" in expectancy_df.columns
        assert len(expectancy_df) == len(pd.date_range(min_date, max_date)) - 30
        assert round(expectancy_df["expectancy"].iloc[-1], 2) == expected_result_absolute
        assert round(expectancy_df["expectancy_pct"].iloc[-1], 5) == expected_result_relative
