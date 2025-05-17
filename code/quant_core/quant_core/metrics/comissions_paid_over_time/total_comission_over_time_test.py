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

    def test_ungrouped_result_cum_sum(self) -> None:
        data_frame = Builder.get_trade_history()

        commission_df = CommissionOverTime().calculate(
            data_frame,
            group_by_account_id=False,
            group_by_symbol=False,
            cum_sum=True,
        )

        assert commission_df["time"].is_monotonic_increasing
        assert commission_df["total_commission"].is_monotonic_decreasing
        assert "account_id" not in commission_df.columns
        assert "symbol" not in commission_df.columns
        assert round(commission_df["total_commission"].iloc[-1], 2) == -282.15

    def test_grouped_by_account_result_cum_sum(self) -> None:
        data_frame = Builder.get_trade_history()
        # Verified manual calculation
        account_results = {
            "A2NRRYL4": -257.55,
            "0EUEV5SO": -24.6,
            "46TGTINM": 0.0,
        }

        commission_df = CommissionOverTime().calculate(
            data_frame, group_by_account_id=True, group_by_symbol=False, cum_sum=True
        )

        assert "account_id" in commission_df.columns
        assert "symbol" not in commission_df.columns
        assert "total_commission" in commission_df.columns

        for account_id in commission_df["account_id"].unique():
            account_commission_df = commission_df[commission_df["account_id"] == account_id]
            assert account_commission_df["time"].is_monotonic_increasing
            assert account_commission_df["total_commission"].is_monotonic_decreasing
            assert len(account_commission_df) > 0
            assert round(account_commission_df.iloc[-1]["total_commission"], 2) == account_results[account_id]

    def test_grouped_by_symbol_result_cum_sum(self) -> None:
        data_frame = Builder.get_trade_history()
        # Verified manual calculation
        symbol_results = {
            "ADAUSD": 0.0,
            "AUS200.cash": 0.0,
            "AUDCAD": 0.0,
            "AUDJPY": -17.59,
            "AUDUSD": -7.58,
            "BTCUSD": 0.0,
            "DOTUSD": 0.0,
            "EURAUD": -11.4,
            "EURGBP": -9.74,
            "EURJPY": -45.07,
            "EURUSD": -60.29,
            "ETHUSD": 0.0,
            "EU50.cash": 0.0,
            "FRA40.cash": 0.0,
            "GBPAUD": -7.8,
            "GBPJPY": -4.7,
            "GBPUSD": -19.99,
            "GER40.cash": 0.0,
            "NZDUSD": -8.36,
            "UK100.cash": 0.0,
            "US100.cash": 0.0,
            "US500.cash": 0.0,
            "USDCAD": -13.89,
            "USDCHF": -17.38,
            "USDJPY": -32.75,
            "XAUUSD": -25.61,
            "XRPUSD": 0.0,
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
            assert symbol_commission_df["time"].is_monotonic_increasing
            assert symbol_commission_df["total_commission"].is_monotonic_decreasing
            assert len(symbol_commission_df) > 0
            assert round(symbol_commission_df.iloc[-1]["total_commission"], 2) == symbol_results[symbol]

    def test_grouped_by_account_and_symbol_result_cum_sum(self) -> None:
        data_frame = Builder.get_trade_history()
        # Verified manual calculation
        account_symbol_results = {
            "A2NRRYL4": {
                "ADAUSD": 0.0,
                "AUDJPY": -16.77,
                "AUDUSD": -6.46,
                "AUS200.cash": 0.0,
                "BTCUSD": 0.0,
                "DOTUSD": 0.0,
                "EURAUD": -9.32,
                "EURGBP": -8.6,
                "EURJPY": -43.43,
                "EURUSD": -57.19,
                "ETHUSD": 0.0,
                "EU50.cash": 0.0,
                "FRA40.cash": 0.0,
                "GBPAUD": -6.4,
                "GBPJPY": -3.66,
                "GBPUSD": -16.29,
                "NZDUSD": -6.86,
                "US100.cash": 0.0,
                "USDCAD": -12.05,
                "USDCHF": -15.28,
                "USDJPY": -30.19,
                "UK100.cash": 0.0,
                "XAUUSD": -25.05,
                "XRPUSD": 0.0,
            },
            "0EUEV5SO": {
                "AUS200.cash": 0.0,
                "AUDJPY": -0.82,
                "AUDUSD": -1.12,
                "BTCUSD": 0.0,
                "EURAUD": -2.08,
                "EURGBP": -1.14,
                "EURJPY": -1.64,
                "EURUSD": -3.1,
                "EU50.cash": 0.0,
                "GBPAUD": -1.4,
                "GBPJPY": -1.04,
                "GBPUSD": -3.7,
                "NZDUSD": -1.5,
                "US100.cash": 0.0,
                "USDCAD": -1.84,
                "USDCHF": -2.1,
                "USDJPY": -2.56,
                "UK100.cash": 0.0,
                "XAUUSD": -0.56,
                "ETHUSD": 0.0,
            },
            "46TGTINM": {
                "GER40.cash": 0.0,
                "US500.cash": 0.0,
            },
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

    def test_ungrouped_result_no_cum_sum_days(self) -> None:
        data_frame = Builder.get_trade_history()
        data_frame = CommissionOverTime()._normalize_time(data_frame)
        min_date = data_frame["time"].min().replace(hour=0, minute=0, second=0, microsecond=0)
        max_date = data_frame["time"].max().replace(hour=0, minute=0, second=0, microsecond=0)

        commission_df = CommissionOverTime().calculate(
            data_frame,
            group_by_account_id=False,
            group_by_symbol=False,
            cum_sum=False,
        )

        assert commission_df["time"].is_monotonic_increasing
        assert "account_id" not in commission_df.columns
        assert "symbol" not in commission_df.columns
        assert "total_commission" in commission_df.columns
        assert len(commission_df) == len(pd.date_range(min_date, max_date))
        assert round(commission_df["total_commission"].iloc[-1], 2) == -48.85
