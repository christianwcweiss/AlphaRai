from itertools import combinations

import numpy as np
import pandas as pd
import pytest

from quant_core.metrics.account_balance_over_time.balance_over_time import AccountBalanceOverTime
from quant_dev.builder import Builder


class TestAccountBalanceOverTimeAbsolute:

    @pytest.mark.parametrize(
        "group_by_account_id,group_by_symbol, group_by_hour, group_by_weekday",
        [
            tuple(
                i in combination for i in range(4)
            ) for r in range(5) for combination in combinations(range(4), r)
        ]
    )
    def test_columns_in_data_frame(
            self,
            group_by_account_id: bool,
            group_by_symbol: bool,
            group_by_hour: bool,
            group_by_weekday: bool,
    ) -> None:
        data_frame = Builder.get_trade_history()

        balance_df = AccountBalanceOverTime().calculate(
            data_frame,
            group_by_account_id=group_by_account_id,
            group_by_symbol=group_by_symbol,
            group_by_hour=group_by_hour,
            group_by_weekday=group_by_weekday,
        )

        assert "initial_balance" in balance_df.columns
        assert "absolute_balance" in balance_df.columns
        assert "relative_balance" in balance_df.columns
        assert len(balance_df) == len(data_frame)

        if group_by_account_id:
            assert "account_id" in balance_df.columns

        if group_by_symbol:
            assert "symbol" in balance_df.columns

        if group_by_hour:
            assert "open_hour" in balance_df.columns

        if group_by_weekday:
            assert "open_weekday" in balance_df.columns

    def test_rolling_window_days_do_not_have_effect(self) -> None:
        data_frame = Builder.get_trade_history()
        rolling_window = Builder.build_random_int()

        balance_df = AccountBalanceOverTime().calculate(
            data_frame,
            group_by_account_id=Builder.build_random_bool(),
            group_by_symbol=Builder.build_random_bool(),
            group_by_hour=Builder.build_random_bool(),
            group_by_weekday=Builder.build_random_bool(),
            rolling_window=rolling_window,
        )

        assert "initial_balance" in balance_df.columns
        assert "absolute_balance" in balance_df.columns
        assert "relative_balance" in balance_df.columns
        assert len(balance_df) == len(data_frame)

    @pytest.mark.parametrize("expected_result_absolute,expected_result_relative", [((90133.55, 100.15))])
    def test_ungrouped_result(self, expected_result_absolute: float, expected_result_relative: float) -> None:
        data_frame = Builder.get_trade_history()

        balance_df = AccountBalanceOverTime().calculate(
            data_frame,
            group_by_account_id=False,
            group_by_symbol=False,
        )

        assert "account_id" not in balance_df.columns
        assert "symbol" not in balance_df.columns
        assert "initial_balance" in balance_df.columns
        assert "absolute_balance" in balance_df.columns
        assert "relative_balance" in balance_df.columns
        assert round(balance_df.iloc[-1]["absolute_balance"], 2) == expected_result_absolute
        assert round(balance_df.iloc[-1]["relative_balance"], 2) == expected_result_relative

    def test_grouped_by_account_result(self) -> None:
        data_frame = Builder.get_trade_history()
        # Verified manual calculation
        account_results_absolute = {
            "A2NRRYL4": 80004.81,
            "0EUEV5SO": 10133.55,
        }
        account_results_relative = {
            "A2NRRYL4": 100.01,
            "0EUEV5SO": 101.34,
        }

        balance_df = AccountBalanceOverTime().calculate(
            data_frame,
            group_by_account_id=True,
            group_by_symbol=False,
            group_by_hour=False,
            group_by_weekday=False,
        )

        assert "account_id" in balance_df.columns
        assert "symbol" not in balance_df.columns
        assert "open_hour" not in balance_df.columns
        assert "open_weekday" not in balance_df.columns
        assert "initial_balance" in balance_df.columns
        assert "absolute_balance" in balance_df.columns
        assert "relative_balance" in balance_df.columns

        for account_id in balance_df["account_id"].unique():
            account_balance_df = balance_df[balance_df["account_id"] == account_id]
            assert len(account_balance_df) > 0
            assert round(account_balance_df.iloc[-1]["absolute_balance"], 2) == account_results_absolute[account_id]
            assert round(account_balance_df.iloc[-1]["relative_balance"], 2) == account_results_relative[account_id]

    def test_grouped_by_symbol_result(self) -> None:
        data_frame = Builder.get_trade_history()
        # Verified manual calculation
        symbol_results_absolute = {
            "EURUSD": 87540.74,
            "GBPUSD": 91181.49,
            "USDCHF": 90113.2,
            "USDJPY": 90010.76,
        }
        symbol_results_relative = {
            "EURUSD": 97.27,
            "GBPUSD": 101.31,
            "USDCHF": 100.13,
            "USDJPY": 100.01,
        }

        balance_df = AccountBalanceOverTime().calculate(
            data_frame,
            group_by_account_id=False,
            group_by_symbol=True,
        )

        assert "account_id" not in balance_df.columns
        assert "symbol" in balance_df.columns
        assert "open_hour" not in balance_df.columns
        assert "open_weekday" not in balance_df.columns
        assert "initial_balance" in balance_df.columns
        assert "absolute_balance" in balance_df.columns
        assert "relative_balance" in balance_df.columns

        for symbol in balance_df["symbol"].unique():
            if symbol is np.nan:
                continue

            symbol_balance_df = balance_df[balance_df["symbol"] == symbol]
            assert len(symbol_balance_df) > 0, f"No data for symbol {symbol}"
            assert round(symbol_balance_df.iloc[-1]["absolute_balance"], 2) == symbol_results_absolute[symbol], (
                f"Expected {symbol_results_absolute[symbol]} for symbol {symbol}, "
                f"but got {round(symbol_balance_df.iloc[-1]['absolute_balance'], 2)}"
            )
            assert round(symbol_balance_df.iloc[-1]["relative_balance"], 2) == symbol_results_relative[symbol], (
                f"Expected {symbol_results_relative[symbol]} for symbol {symbol}, "
                f"but got {round(symbol_balance_df.iloc[-1]['relative_balance'], 2)}"
            )

    def test_grouped_by_hour_result(self) -> None:
        data_frame = Builder.get_trade_history()

        # Expected end-of-hour balances (verified)
        hour_results_absolute = {
            0: 90179.56,
            1: 89847.24,
            2: 90001.67,
            3: 90011.26,
            5: 90000.85,
            6: 89998.38,
            9: 89905.87,
            10: 89981.48,
            11: 90077.17,
            12: 89769.06,
            13: 89971.37,
            14: 90034.56,
            15: 89931.41,
            16: 90296.57,
            17: 90241.32,
            18: 90786.08,
            19: 90003.5,
            20: 89961.67,
            21: 89991.43,
            22: 90027.64,
            23: 89996.03,
        }
        hour_results_relative = {
            0: 100.2,
            1: 99.83,
            2: 100.0,
            3: 100.01,
            5: 100.0,
            6: 100.0,
            9: 99.9,
            10: 99.98,
            11: 100.09,
            12: 99.74,
            13: 99.97,
            14: 100.04,
            15: 99.92,
            16: 100.33,
            17: 100.27,
            18: 100.87,
            19: 100.0,
            20: 99.96,
            21: 99.99,
            22: 100.03,
            23: 100.0,
        }

        balance_df = AccountBalanceOverTime().calculate(
            data_frame,
            group_by_account_id=False,
            group_by_symbol=False,
            group_by_hour=True,
            group_by_weekday=False,
        )

        assert "account_id" not in balance_df.columns
        assert "symbol" not in balance_df.columns
        assert "open_hour" in balance_df.columns
        assert "open_weekday" not in balance_df.columns
        assert "initial_balance" in balance_df.columns
        assert "absolute_balance" in balance_df.columns
        assert "relative_balance" in balance_df.columns

        for hour in balance_df["open_hour"].unique():
            if pd.isna(hour):
                continue

            hour_balance_df = balance_df[balance_df["open_hour"] == hour]
            assert len(hour_balance_df) > 0, f"No data for hour {hour}"
            assert round(hour_balance_df.iloc[-1]["absolute_balance"], 2) == hour_results_absolute[hour], (
                f"Expected {hour_results_absolute[hour]} for hour {hour}, "
                f"but got {round(hour_balance_df.iloc[-1]['absolute_balance'], 2)}"
            )
            assert round(hour_balance_df.iloc[-1]["relative_balance"], 2) == hour_results_relative[hour], (
                f"Expected {hour_results_relative[hour]} for hour {hour}, "
                f"but got {round(hour_balance_df.iloc[-1]['relative_balance'], 2)}"
            )

    def test_grouped_by_weekday_result(self) -> None:
        data_frame = Builder.get_trade_history()

        # Expected end-of-weekday balances (verified)
        weekday_results_absolute = {
            0: 89959.41,  # Monday
            1: 90239.85,  # Tuesday
            2: 90601.3,  # Wednesday
            3: 88776.81,  # Thursday
            4: 90568.78,  # Friday
        }
        weekday_results_relative = {
            0: 99.95,
            1: 100.27,
            2: 100.67,
            3: 98.64,
            4: 100.63,
        }

        balance_df = AccountBalanceOverTime().calculate(
            data_frame,
            group_by_account_id=False,
            group_by_symbol=False,
            group_by_hour=False,
            group_by_weekday=True,
        )

        assert "account_id" not in balance_df.columns
        assert "symbol" not in balance_df.columns
        assert "open_hour" not in balance_df.columns
        assert "open_weekday" in balance_df.columns
        assert "initial_balance" in balance_df.columns
        assert "absolute_balance" in balance_df.columns
        assert "relative_balance" in balance_df.columns

        for weekday in balance_df["open_weekday"].unique():
            if pd.isna(weekday):
                continue

            weekday_balance_df = balance_df[balance_df["open_weekday"] == weekday]
            assert len(weekday_balance_df) > 0, f"No data for weekday {weekday}"
            assert round(weekday_balance_df.iloc[-1]["absolute_balance"], 2) == weekday_results_absolute[weekday], (
                f"Expected {weekday_results_absolute[weekday]} for weekday {weekday}, "
                f"but got {round(weekday_balance_df.iloc[-1]['absolute_balance'], 2)}"
            )
            assert round(weekday_balance_df.iloc[-1]["relative_balance"], 2) == weekday_results_relative[weekday], (
                f"Expected {weekday_results_relative[weekday]} for weekday {weekday}, "
                f"but got {round(weekday_balance_df.iloc[-1]['relative_balance'], 2)}"
            )

    def test_grouped_by_account_and_symbol(self) -> None:
        data_frame = Builder.get_trade_history()
        # Verified manual calculation
        account_symbol_results_absolute = {
            "A2NRRYL4": {
                "EURUSD": 77726.55,
                "GBPUSD": 80987.55,
                "USDCHF": 80685.67,
                "USDJPY": 80778.17,
            },
            "0EUEV5SO": {
                "EURUSD": 9814.19,
                "GBPUSD": 10216.53,
                "USDCHF": 10113.2,
                "USDJPY": 10010.76,
            },
        }
        account_symbol_results_relative = {
            "A2NRRYL4": {
                "EURUSD": 97.16,
                "GBPUSD": 101.23,
                "USDCHF": 100.86,
                "USDJPY": 100.97,
            },
            "0EUEV5SO": {
                "EURUSD": 98.14,
                "GBPUSD": 102.17,
                "USDCHF": 101.13,
                "USDJPY": 100.11,
            },
        }

        balance_df = AccountBalanceOverTime().calculate(
            data_frame,
            group_by_account_id=True,
            group_by_symbol=True,
        )

        assert "account_id" in balance_df.columns
        assert "symbol" in balance_df.columns
        assert "open_hour" not in balance_df.columns
        assert "open_weekday" not in balance_df.columns
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
                    == account_symbol_results_absolute[account_id][symbol]
                ), (
                    f"Expected {account_symbol_results_absolute[account_id][symbol]} "
                    f"for account {account_id} and symbol {symbol}, "
                    f"but got {round(account_symbol_balance_df.iloc[-1]['absolute_balance'], 2)}"
                )
                assert (
                    round(account_symbol_balance_df.iloc[-1]["relative_balance"], 2)
                    == account_symbol_results_relative[account_id][symbol]
                ), (
                    f"Expected {account_symbol_results_relative[account_id][symbol]} "
                    f"for account {account_id} and symbol {symbol}, "
                    f"but got {round(account_symbol_balance_df.iloc[-1]['relative_balance'], 2)}"
                )
