import numpy as np
import pandas as pd
import pytest

from quant_core.metrics.comissions_paid_over_time.total_comission_over_time import CommissionOverTime
from quant_dev.builder import Builder


class TestCommissionOverTime:
    @pytest.mark.parametrize(
        "group_by_account_id,group_by_symbol,cum_sum",
        [
            (True, False, True),
            (False, True, True),
            (True, True, True),
            (True, False, False),
            (False, True, False),
            (True, True, False),
        ],
    )
    def test_columns_in_data_frame(
        self,
        group_by_account_id: bool,
        group_by_symbol: bool,
        cum_sum: bool,
    ) -> None:
        data_frame = Builder.get_trade_history()

        commission_df = CommissionOverTime().calculate(
            data_frame,
            group_by_account_id=group_by_account_id,
            group_by_symbol=group_by_symbol,
            cum_sum=cum_sum,
        )

        assert "total_commission" in commission_df.columns
        if cum_sum:  # else case is handled indirectly by the other tests
            assert len(commission_df) == len(data_frame)

        if group_by_account_id:
            assert "account_id" in commission_df.columns

        if group_by_symbol:
            assert "symbol" in commission_df.columns

    def test_rolling_window_days_do_not_have_effect_cum_sum(self) -> None:
        data_frame = Builder.get_trade_history()
        rolling_window_days = Builder.build_random_int()

        commission_df = CommissionOverTime().calculate(
            data_frame,
            group_by_account_id=Builder.build_random_bool(),
            group_by_symbol=Builder.build_random_bool(),
            rolling_window=rolling_window_days,
            cum_sum=True,
        )

        assert len(commission_df) == len(data_frame)

    @pytest.mark.parametrize(
        "expected_result", [-83.08]
    )
    def test_ungrouped_result_cum_sum(self, expected_result: float) -> None:
        data_frame = Builder.get_trade_history()

        commission_df = CommissionOverTime().calculate(
            data_frame,
            group_by_account_id=False,
            group_by_symbol=False,
            cum_sum=True,
        )

        assert commission_df["total_commission"].is_monotonic_decreasing
        assert "account_id" not in commission_df.columns
        assert "symbol" not in commission_df.columns
        assert round(commission_df["total_commission"].iloc[-1], 2) == expected_result

    def test_grouped_by_account_result_cum_sum(self) -> None:
        data_frame = Builder.get_trade_history()
        # Verified manual calculation
        account_results = {
            "A2NRRYL4": -74.48,
            "0EUEV5SO": -8.6,
        }

        commission_df = CommissionOverTime().calculate(
            data_frame, group_by_account_id=True, group_by_symbol=False, cum_sum=True
        )

        assert "account_id" in commission_df.columns
        assert "symbol" not in commission_df.columns
        assert "total_commission" in commission_df.columns

        for account_id in commission_df["account_id"].unique():
            account_commission_df = commission_df[commission_df["account_id"] == account_id]
            assert account_commission_df["total_commission"].is_monotonic_decreasing
            assert len(account_commission_df) > 0
            assert round(account_commission_df.iloc[-1]["total_commission"], 2) == account_results[account_id]

    def test_grouped_by_symbol_result_cum_sum(self) -> None:
        data_frame = Builder.get_trade_history()
        # Verified manual calculation
        symbol_results = {
                "EURUSD": -36.36,
                "GBPUSD": -13.96,
                "USDCHF": -16.15,
                "USDJPY": -16.61,
            }

        commission_df = CommissionOverTime().calculate(
            data_frame, group_by_account_id=False, group_by_symbol=True, cum_sum=True
        )

        assert "account_id" not in commission_df.columns
        assert "symbol" in commission_df.columns
        assert "total_commission" in commission_df.columns

        for symbol in commission_df["symbol"].unique():
            if symbol is np.nan:
                continue

            symbol_commission_df = commission_df[commission_df["symbol"] == symbol]
            assert symbol_commission_df["total_commission"].is_monotonic_decreasing
            assert len(symbol_commission_df) > 0
            assert round(symbol_commission_df.iloc[-1]["total_commission"], 2) == symbol_results[symbol]

    def test_grouped_by_account_and_symbol_result_cum_sum(self) -> None:
        data_frame = Builder.get_trade_history()
        # Verified manual calculation
        account_symbol_results = {
            "A2NRRYL4": {
                "EURUSD": -34.47,
                "GBPUSD": -11.55,
                "USDCHF": -13.23,
                "USDJPY": -15.23,
            },
            "0EUEV5SO": {
                "EURUSD": -1.89,
                "GBPUSD": -2.41,
                "USDCHF": -2.92,
                "USDJPY": -1.38,
            }
        }

        commission_df = CommissionOverTime().calculate(
            data_frame, group_by_account_id=True, group_by_symbol=True, cum_sum=True
        )

        assert "account_id" in commission_df.columns
        assert "symbol" in commission_df.columns
        assert "total_commission" in commission_df.columns

        for account_id in commission_df["account_id"].unique():
            for symbol in commission_df[commission_df["account_id"] == account_id]["symbol"].unique():
                if symbol is np.nan:
                    continue

                account_symbol_commission_df = commission_df[
                    (commission_df["account_id"] == account_id) & (commission_df["symbol"] == symbol)
                ]
                assert len(account_symbol_commission_df) > 0
                assert (
                    round(account_symbol_commission_df.iloc[-1]["total_commission"], 2)
                    == account_symbol_results[account_id][symbol]
                ), (
                    f"Expected {account_symbol_results[account_id][symbol]} "
                    f"for account {account_id} and symbol {symbol}, "
                    f"but got {round(account_symbol_commission_df.iloc[-1]['total_commission'], 2)}"
                )

    @pytest.mark.parametrize(
        "expected_result", [-8.65]
    )
    def test_ungrouped_result_no_cum_sum_days(self, expected_result: float) -> None:
        data_frame = Builder.get_trade_history()
        data_frame = CommissionOverTime()._normalize_time(data_frame)
        min_date = data_frame["opened_at"].min().replace(hour=0, minute=0, second=0, microsecond=0)
        max_date = data_frame["closed_at"].max().replace(hour=0, minute=0, second=0, microsecond=0)

        commission_df = CommissionOverTime().calculate(
            data_frame,
            group_by_account_id=False,
            group_by_symbol=False,
            cum_sum=False,
            aggregation_resolution="D"
        )

        assert commission_df["closed_at"].is_monotonic_increasing
        assert "account_id" not in commission_df.columns
        assert "symbol" not in commission_df.columns
        assert "total_commission" in commission_df.columns
        assert len(commission_df) == len(pd.date_range(min_date, max_date))
        assert round(commission_df["total_commission"].iloc[-1], 2) == expected_result
