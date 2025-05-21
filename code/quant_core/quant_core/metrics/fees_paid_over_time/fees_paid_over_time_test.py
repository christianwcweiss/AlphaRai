import numpy as np
import pandas as pd
import pytest

from quant_core.metrics.fees_paid_over_time.fees_paid_over_time import FeesOverTime
from quant_dev.builder import Builder


class TestFeesOverTime:
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

        fee_df = FeesOverTime().calculate(
            data_frame,
            group_by_account_id=group_by_account_id,
            group_by_symbol=group_by_symbol,
            cum_sum=cum_sum,
        )

        assert "total_commission" in fee_df.columns
        assert "total_swap" in fee_df.columns
        assert "total_fees" in fee_df.columns
        if cum_sum:  # else case is handled indirectly by the other tests
            assert len(fee_df) == len(data_frame)

        if group_by_account_id:
            assert "account_id" in fee_df.columns

        if group_by_symbol:
            assert "symbol" in fee_df.columns

    def test_rolling_window_days_do_not_have_effect_cum_sum(self) -> None:
        data_frame = Builder.get_trade_history()
        rolling_window_days = Builder.build_random_int()

        fee_df = FeesOverTime().calculate(
            data_frame,
            group_by_account_id=Builder.build_random_bool(),
            group_by_symbol=Builder.build_random_bool(),
            rolling_window=rolling_window_days,
            cum_sum=True,
        )

        assert len(fee_df) == len(data_frame)

    @pytest.mark.parametrize("expected_result", [-167.01])
    def test_ungrouped_result_cum_sum(self, expected_result: float) -> None:
        data_frame = Builder.get_trade_history()

        fee_df = FeesOverTime().calculate(
            data_frame,
            group_by_account_id=False,
            group_by_symbol=False,
            cum_sum=True,
        )

        assert fee_df["total_commission"].is_monotonic_decreasing
        assert all(row["total_fees"] == row["total_commission"] + row["total_swap"] for _, row in fee_df.iterrows())
        assert "account_id" not in fee_df.columns
        assert "symbol" not in fee_df.columns
        assert round(fee_df["total_commission"].iloc[-1], 2) == expected_result

    def test_grouped_by_account_result_cum_sum(self) -> None:
        data_frame = Builder.get_trade_history()
        # Verified manual calculation
        account_results_commission = {
            "A2NRRYL4": -149.48,
            "0EUEV5SO": -17.53,
        }
        account_results_swap = {
            "A2NRRYL4": -22.36,
            "0EUEV5SO": -4.68,
        }

        fee_df = FeesOverTime().calculate(data_frame, group_by_account_id=True, group_by_symbol=False, cum_sum=True)

        assert "account_id" in fee_df.columns
        assert "symbol" not in fee_df.columns
        assert "total_commission" in fee_df.columns
        assert "total_swap" in fee_df.columns
        assert "total_fees" in fee_df.columns

        for account_id in fee_df["account_id"].unique():
            account_fee_df = fee_df[fee_df["account_id"] == account_id]
            assert account_fee_df["total_commission"].is_monotonic_decreasing
            assert len(account_fee_df) > 0
            assert round(account_fee_df.iloc[-1]["total_commission"], 2) == account_results_commission[account_id]
            assert round(account_fee_df.iloc[-1]["total_swap"], 2) == account_results_swap[account_id]
            assert round(account_fee_df.iloc[-1]["total_fees"], 2) == round(
                account_results_commission[account_id] + account_results_swap[account_id], 2
            )

    def test_grouped_by_symbol_result_cum_sum(self) -> None:
        data_frame = Builder.get_trade_history()
        # Verified manual calculation
        symbol_results_commission = {
            "EURUSD": -36.36,
            "GBPUSD": -13.96,
            "USDCHF": -16.15,
            "USDJPY": -33.22,
        }
        symbol_results_swap = {
            "EURUSD": -36.36,
            "GBPUSD": -13.96,
            "USDCHF": -16.15,
            "USDJPY": -33.22,
        }

        fee_df = FeesOverTime().calculate(data_frame, group_by_account_id=False, group_by_symbol=True, cum_sum=True)

        assert "account_id" not in fee_df.columns
        assert "symbol" in fee_df.columns
        assert "total_commission" in fee_df.columns
        assert "total_swap" in fee_df.columns
        assert "total_fees" in fee_df.columns

        for symbol in fee_df["symbol"].unique():
            if symbol is np.nan:
                continue

            symbol_fee_df = fee_df[fee_df["symbol"] == symbol]
            assert symbol_fee_df["total_commission"].is_monotonic_decreasing
            assert len(symbol_fee_df) > 0
            assert round(symbol_fee_df.iloc[-1]["total_commission"], 2) == symbol_results_commission[symbol]
            assert round(symbol_fee_df.iloc[-1]["total_swap"], 2) == symbol_results_swap[symbol]
            assert round(symbol_fee_df.iloc[-1]["total_fees"], 2) == round(
                symbol_results_commission[symbol] + symbol_results_swap[symbol], 2
            )

    def test_grouped_by_account_and_symbol_result_cum_sum(self) -> None:
        data_frame = Builder.get_trade_history()
        # Verified manual calculation
        account_symbol_results_commission = {
            "A2NRRYL4": {
                "EURUSD": -68.93,
                "GBPUSD": -23.05,
                "USDCHF": -27.04,
                "USDJPY": -30.46,
            },
            "0EUEV5SO": {
                "EURUSD": -3.78,
                "GBPUSD": -4.82,
                "USDCHF": -6.17,
                "USDJPY": -2.76,
            },
        }
        account_symbol_results_swap = {
            "A2NRRYL4": {
                "EURUSD": 5.04,
                "GBPUSD": -8.95,
                "USDCHF": -12.45,
                "USDJPY": -6,
            },
            "0EUEV5SO": {
                "EURUSD": 1.2,
                "GBPUSD": -1.88,
                "USDCHF": -2.11,
                "USDJPY": -1.89,
            },
        }

        fee_df = FeesOverTime().calculate(data_frame, group_by_account_id=True, group_by_symbol=True, cum_sum=True)

        assert "account_id" in fee_df.columns
        assert "symbol" in fee_df.columns
        assert "total_commission" in fee_df.columns
        assert "total_swap" in fee_df.columns
        assert "total_fees" in fee_df.columns

        for account_id in fee_df["account_id"].unique():
            for symbol in fee_df[fee_df["account_id"] == account_id]["symbol"].unique():
                if symbol is np.nan:
                    continue

                account_symbol_fee_df = fee_df[(fee_df["account_id"] == account_id) & (fee_df["symbol"] == symbol)]
                assert len(account_symbol_fee_df) > 0
                assert (
                    round(account_symbol_fee_df.iloc[-1]["total_commission"], 2)
                    == account_symbol_results_commission[account_id][symbol]
                ), (
                    f"Expected {account_symbol_results_commission[account_id][symbol]} "
                    f"for account {account_id} and symbol {symbol}, "
                    f"but got {round(account_symbol_fee_df.iloc[-1]['total_commission'], 2)}"
                )
                assert (
                    round(account_symbol_fee_df.iloc[-1]["total_swap"], 2)
                    == account_symbol_results_swap[account_id][symbol],
                    (
                        f"Expected {account_symbol_results_swap[account_id][symbol]} "
                        f"for account {account_id} and symbol {symbol}, "
                        f"but got {round(account_symbol_fee_df.iloc[-1]['total_swap'], 2)}"
                    ),
                )
                assert round(account_symbol_fee_df.iloc[-1]["total_fees"], 2) == round(
                    account_symbol_results_commission[account_id][symbol]
                    + account_symbol_results_swap[account_id][symbol],
                    2,
                )

    @pytest.mark.parametrize("expected_result_commission,expected_result_swap", [(-16.94, -0.26)])
    def test_ungrouped_result_no_cum_sum_days(
        self, expected_result_commission: float, expected_result_swap: float
    ) -> None:
        data_frame = Builder.get_trade_history()
        data_frame = FeesOverTime()._normalize_time(data_frame)
        min_date = data_frame["opened_at"].min().replace(hour=0, minute=0, second=0, microsecond=0)
        max_date = data_frame["closed_at"].max().replace(hour=0, minute=0, second=0, microsecond=0)

        fee_df = FeesOverTime().calculate(
            data_frame, group_by_account_id=False, group_by_symbol=False, cum_sum=False, aggregation_resolution="D"
        )

        assert fee_df["closed_at"].is_monotonic_increasing
        assert "account_id" not in fee_df.columns
        assert "symbol" not in fee_df.columns
        assert "total_commission" in fee_df.columns
        assert "total_swap" in fee_df.columns
        assert "total_fees" in fee_df.columns
        assert len(fee_df) == len(pd.date_range(min_date, max_date))
        assert round(fee_df["total_commission"].iloc[-1], 2) == expected_result_commission
        assert round(fee_df["total_swap"].iloc[-1], 2) == expected_result_swap
        assert round(fee_df["total_fees"].iloc[-1], 2) == round(expected_result_commission + expected_result_swap, 2)
