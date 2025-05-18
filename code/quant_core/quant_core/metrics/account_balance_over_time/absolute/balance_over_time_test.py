import numpy as np
import pytest

from quant_core.metrics.account_balance_over_time.absolute.balance_over_time import AccountBalanceOverTimeAbsolute
from quant_dev.builder import Builder


class TestAccountBalanceOverTimeAbsolute:

    @pytest.mark.parametrize("group_by_account_id,group_by_symbol", [(True, False), (False, True), (True, True)])
    def test_columns_in_data_frame(self, group_by_account_id: bool, group_by_symbol: bool) -> None:
        data_frame = Builder.get_trade_history()

        balance_df = AccountBalanceOverTimeAbsolute().calculate(
            data_frame,
            group_by_account_id=group_by_account_id,
            group_by_symbol=group_by_symbol,
        )

        assert "initial_balance" in balance_df.columns
        assert "absolute_balance" in balance_df.columns
        assert len(balance_df) == len(data_frame)

        if group_by_account_id:
            assert "account_id" in balance_df.columns

        if group_by_symbol:
            assert "symbol" in balance_df.columns

    def test_rolling_window_days_do_not_have_effect(self) -> None:
        data_frame = Builder.get_trade_history()
        rolling_window_days = Builder.build_random_int()

        balance_df = AccountBalanceOverTimeAbsolute().calculate(
            data_frame,
            group_by_account_id=Builder.build_random_bool(),
            group_by_symbol=Builder.build_random_bool(),
            rolling_window_days=rolling_window_days,
        )

        assert "initial_balance" in balance_df.columns
        assert "absolute_balance" in balance_df.columns
        assert len(balance_df) == len(data_frame)

    @pytest.mark.parametrize("expected_result", [90302.48])
    def test_ungrouped_result(self, expected_result: float) -> None:
        data_frame = Builder.get_trade_history()

        balance_df = AccountBalanceOverTimeAbsolute().calculate(
            data_frame,
            group_by_account_id=False,
            group_by_symbol=False,
        )

        assert "account_id" not in balance_df.columns
        assert "symbol" not in balance_df.columns
        assert "initial_balance" in balance_df.columns
        assert "absolute_balance" in balance_df.columns
        assert round(balance_df.iloc[-1]["absolute_balance"], 2) == expected_result

    def test_grouped_by_account_result(self) -> None:
        data_frame = Builder.get_trade_history()
        # Verified manual calculation
        account_results = {
            "A2NRRYL4": 80148.94,
            "0EUEV5SO": 10153.54,
        }

        balance_df = AccountBalanceOverTimeAbsolute().calculate(
            data_frame,
            group_by_account_id=True,
            group_by_symbol=False,
        )

        assert "account_id" in balance_df.columns
        assert "symbol" not in balance_df.columns
        assert "initial_balance" in balance_df.columns
        assert "absolute_balance" in balance_df.columns

        for account_id in balance_df["account_id"].unique():
            account_balance_df = balance_df[balance_df["account_id"] == account_id]
            assert len(account_balance_df) > 0
            assert round(account_balance_df.iloc[-1]["absolute_balance"], 2) == account_results[account_id]

    def test_grouped_by_symbol_result(self) -> None:
        data_frame = Builder.get_trade_history()
        # Verified manual calculation
        symbol_results = {
            "EURUSD": 87577.09,
            "GBPUSD": 91022.27,
            "USDCHF": 90815.93,
            "USDJPY": 90807.0,
        }

        balance_df = AccountBalanceOverTimeAbsolute().calculate(
            data_frame,
            group_by_account_id=False,
            group_by_symbol=True,
        )

        assert "account_id" not in balance_df.columns
        assert "symbol" in balance_df.columns
        assert "initial_balance" in balance_df.columns
        assert "absolute_balance" in balance_df.columns

        for symbol in balance_df["symbol"].unique():
            if symbol is np.nan:
                continue

            symbol_balance_df = balance_df[balance_df["symbol"] == symbol]
            assert len(symbol_balance_df) > 0, f"No data for symbol {symbol}"
            assert round(symbol_balance_df.iloc[-1]["absolute_balance"], 2) == symbol_results[symbol], (
                f"Expected {symbol_results[symbol]} for symbol {symbol}, "
                f"but got {round(symbol_balance_df.iloc[-1]['absolute_balance'], 2)}"
            )

    def test_grouped_by_account_and_symbol(self) -> None:
        data_frame = Builder.get_trade_history()
        # Verified manual calculation
        account_symbol_results = {
            "A2NRRYL4": {
                "EURUSD": 77761.01,
                "GBPUSD": 80825.92,
                "USDCHF": 80699.48,
                "USDJPY": 80793.4,
            },
            "0EUEV5SO": {
                "EURUSD": 9816.08,
                "GBPUSD": 10196.35,
                "USDCHF": 10116.45,
                "USDJPY": 10013.6,
            },
        }

        balance_df = AccountBalanceOverTimeAbsolute().calculate(
            data_frame,
            group_by_account_id=True,
            group_by_symbol=True,
        )

        assert "account_id" in balance_df.columns
        assert "symbol" in balance_df.columns
        assert "initial_balance" in balance_df.columns
        assert "absolute_balance" in balance_df.columns

        for account_id in balance_df["account_id"].unique():
            for symbol in balance_df[balance_df["account_id"] == account_id]["symbol"].unique():
                if symbol is np.nan:
                    continue

                account_symbol_balance_df = balance_df[
                    (balance_df["account_id"] == account_id) & (balance_df["symbol"] == symbol)
                ]
                assert len(account_symbol_balance_df) > 0
                assert (
                    round(account_symbol_balance_df.iloc[-1]["absolute_balance"], 2)
                    == account_symbol_results[account_id][symbol]
                ), (
                    f"Expected {account_symbol_results[account_id][symbol]} "
                    f"for account {account_id} and symbol {symbol}, "
                    f"but got {round(account_symbol_balance_df.iloc[-1]['absolute_balance'], 2)}"
                )
