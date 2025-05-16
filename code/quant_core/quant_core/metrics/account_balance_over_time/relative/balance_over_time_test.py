import numpy as np
import pytest

from quant_core.metrics.account_balance_over_time.relative.balance_over_time import AccountBalanceOverTimeRelative
from quant_dev.builder import Builder


class TestAccountBalanceOverTimeRelative:

    @pytest.mark.parametrize("group_by_account_id,group_by_symbol", [(True, False), (False, True), (True, True)])
    def test_columns_in_data_frame(self, group_by_account_id: bool, group_by_symbol: bool) -> None:
        data_frame = Builder.get_trade_history()

        balance_df = AccountBalanceOverTimeRelative().calculate(
            data_frame,
            group_by_account_id=group_by_account_id,
            group_by_symbol=group_by_symbol,
        )

        assert "initial_balance" in balance_df.columns
        assert "relative_balance" in balance_df.columns
        assert len(balance_df) == len(data_frame)

        if group_by_account_id:
            assert "account_id" in balance_df.columns

        if group_by_symbol:
            assert "symbol" in balance_df.columns

    def test_rolling_window_days_do_not_have_effect(self) -> None:
        data_frame = Builder.get_trade_history()
        rolling_window_days = Builder.build_random_int()

        balance_df = AccountBalanceOverTimeRelative().calculate(
            data_frame,
            group_by_account_id=Builder.build_random_bool(),
            group_by_symbol=Builder.build_random_bool(),
            rolling_window_days=rolling_window_days,
        )

        assert "initial_balance" in balance_df.columns
        assert "absolute_balance" in balance_df.columns
        assert len(balance_df) == len(data_frame)

    def test_ungrouped_result(self) -> None:
        data_frame = Builder.get_trade_history()

        balance_df = AccountBalanceOverTimeRelative().calculate(
            data_frame,
            group_by_account_id=False,
            group_by_symbol=False,
        )

        assert "account_id" not in balance_df.columns
        assert "symbol" not in balance_df.columns
        assert "initial_balance" in balance_df.columns
        assert balance_df.iloc[-1]["initial_balance"] == 100
        assert "relative_balance" in balance_df.columns
        assert round(balance_df.iloc[-1]["relative_balance"], 2) == 101.04

    def test_grouped_by_account_result(self) -> None:
        data_frame = Builder.get_trade_history()
        # Verified manual calculation
        account_results = {
            "A2NRRYL4": 101.48,
            "0EUEV5SO": 99.07,
            "46TGTINM": 100.24,
        }

        balance_df = AccountBalanceOverTimeRelative().calculate(
            data_frame,
            group_by_account_id=True,
            group_by_symbol=False,
        )

        assert "account_id" in balance_df.columns
        assert "symbol" not in balance_df.columns
        assert "initial_balance" in balance_df.columns
        assert "relative_balance" in balance_df.columns

        for account_id in balance_df["account_id"].unique():
            account_balance_df = balance_df[balance_df["account_id"] == account_id]
            assert len(account_balance_df) > 0
            assert round(account_balance_df.iloc[-1]["relative_balance"], 2) == account_results[account_id]

    def test_grouped_by_symbol_result(self) -> None:
        data_frame = Builder.get_trade_history()
        # Verified manual calculation
        symbol_results = {
            "ADAUSD": 100.03,
            "AUDUSD": 99.22,
            "AUDJPY": 100.45,
            "AUS200.cash": 100.0,
            "BTCUSD": 100.36,
            "DOTUSD": 100.0,
            "ETHUSD": 100.26,
            "EURAUD": 100.32,
            "EURGBP": 100.16,
            "EURJPY": 98.87,
            "EURUSD": 97.52,
            "EU50.cash": 100.01,
            "FRA40.cash": 100.02,
            "GBPAUD": 100.6,
            "GBPJPY": 99.96,
            "GBPUSD": 101.07,
            "GER40.cash": 100.05,
            "USDCAD": 99.71,
            "USDJPY": 100.66,
            "USDCHF": 100.96,
            "NZDUSD": 99.53,
            "UK100.cash": 99.74,
            "US100.cash": 100.26,
            "US500.cash": 100.0,
            "XAUUSD": 101.13,
            "XRPUSD": 100.14,
        }

        balance_df = AccountBalanceOverTimeRelative().calculate(
            data_frame,
            group_by_account_id=False,
            group_by_symbol=True,
        )

        assert "account_id" not in balance_df.columns
        assert "symbol" in balance_df.columns
        assert "initial_balance" in balance_df.columns
        assert "relative_balance" in balance_df.columns

        for symbol in balance_df["symbol"].unique():
            if symbol is np.nan:
                continue

            symbol_balance_df = balance_df[balance_df["symbol"] == symbol]
            assert len(symbol_balance_df) > 0, f"No data for symbol {symbol}"
            assert round(symbol_balance_df.iloc[-1]["relative_balance"], 2) == symbol_results[symbol], (
                f"Expected {symbol_results[symbol]} for symbol {symbol}, "
                f"but got {round(symbol_balance_df.iloc[-1]['relative_balance'], 2)}"
            )

    def test_grouped_by_account_and_symbol(self) -> None:
        data_frame = Builder.get_trade_history()
        # Verified manual calculation
        account_symbol_results = {
            "A2NRRYL4": {
                "ADAUSD": 100.04,
                "AUDJPY": 100.56,
                "AUDUSD": 99.09,
                "AUS200.cash": 100.01,
                "DOTUSD": 100.0,
                "EURAUD": 100.42,
                "EURGBP": 100.2,
                "EURJPY": 98.58,
                "EURUSD": 96.79,
                "EU50.cash": 100.01,
                "FRA40.cash": 100.02,
                "GBPAUD": 100.73,
                "GBPJPY": 99.94,
                "GBPUSD": 101.19,
                "NZDUSD": 99.5,
                "USDCHF": 101.09,
                "USDJPY": 100.92,
                "USDCAD": 99.69,
                "US100.cash": 100.34,
                "UK100.cash": 99.68,
                "XAUUSD": 101.63,
                "XRPUSD": 100.19,
                "BTCUSD": 100.5,
                "ETHUSD": 100.37,
            },
            "0EUEV5SO": {
                "AUS200.cash": 100.0,
                "AUDJPY": 100.55,
                "AUDUSD": 98.64,
                "EURAUD": 100.19,
                "EURGBP": 100.13,
                "EURJPY": 98.96,
                "EURUSD": 98.45,
                "EU50.cash": 100.01,
                "FRA40.cash": 100.02,
                "GBPAUD": 100.79,
                "GBPJPY": 100.01,
                "GBPUSD": 102.25,
                "NZDUSD": 98.88,
                "ETHUSD": 99.96,
                "USDCHF": 101.87,
                "USDJPY": 99.84,
                "USDCAD": 99.28,
                "US100.cash": 100.12,
                "UK100.cash": 99.77,
                "XAUUSD": 99.4,
                "XRPUSD": 100.19,
                "BTCUSD": 99.98,
            },
            "46TGTINM": {
                "GER40.cash": 100.25,
                "US500.cash": 99.99,
            },
        }

        balance_df = AccountBalanceOverTimeRelative().calculate(
            data_frame,
            group_by_account_id=True,
            group_by_symbol=True,
        )

        assert "account_id" in balance_df.columns
        assert "symbol" in balance_df.columns
        assert "initial_balance" in balance_df.columns
        assert "relative_balance" in balance_df.columns

        for account_id in balance_df["account_id"].unique():
            for symbol in balance_df[balance_df["account_id"] == account_id]["symbol"].unique():
                if symbol is np.nan:
                    continue

                account_symbol_balance_df = balance_df[
                    (balance_df["account_id"] == account_id) & (balance_df["symbol"] == symbol)
                ]
                assert len(account_symbol_balance_df) > 0
                assert (
                    round(account_symbol_balance_df.iloc[-1]["relative_balance"], 2)
                    == account_symbol_results[account_id][symbol]
                ), (
                    f"Expected {account_symbol_results[account_id][symbol]} "
                    f"for account {account_id} and symbol {symbol}, "
                    f"but got {round(account_symbol_balance_df.iloc[-1]['relative_balance'], 2)}"
                )
