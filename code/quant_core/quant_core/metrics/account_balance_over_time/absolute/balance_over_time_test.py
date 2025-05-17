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

    def test_ungrouped_result(self) -> None:
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
        assert round(balance_df.iloc[-1]["absolute_balance"], 2) == 111140.95

    def test_grouped_by_account_result(self) -> None:
        data_frame = Builder.get_trade_history()
        # Verified manual calculation
        account_results = {
            "A2NRRYL4": 81186.46,
            "0EUEV5SO": 9906.83,
            "46TGTINM": 20047.66,
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
            "ADAUSD": 110034.5,
            "AUDUSD": 109138.73,
            "AUDJPY": 110500.06,
            "AUS200.cash": 110004.46,
            "BTCUSD": 110394.37,
            "DOTUSD": 110000.1,
            "ETHUSD": 110291.37,
            "EURAUD": 110353.04,
            "EURGBP": 110175.18,
            "EURJPY": 108758.26,
            "EURUSD": 107273.59,
            "EU50.cash": 110010.24,
            "FRA40.cash": 110016.66,
            "GBPAUD": 110661.45,
            "GBPJPY": 109953.27,
            "GBPUSD": 111180.21,
            "GER40.cash": 110050.46,
            "USDCAD": 109675.86,
            "USDJPY": 110723.64,
            "USDCHF": 111058.86,
            "NZDUSD": 109487.98,
            "UK100.cash": 109717.64,
            "US100.cash": 110286.52,
            "US500.cash": 109997.2,
            "XAUUSD": 111248.24,
            "XRPUSD": 110149.06,
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
                "ADAUSD": 80034.5,
                "AUDUSD": 79274.77,
                "AUDJPY": 80445.29,
                "AUS200.cash": 80004.02,
                "BTCUSD": 80396.19,
                "DOTUSD": 80000.1,
                "ETHUSD": 80295.86,
                "EURAUD": 80334.0,
                "EURGBP": 80162.09,
                "EURJPY": 78862.47,
                "EURUSD": 77428.45,
                "EU50.cash": 80009.71,
                "FRA40.cash": 80016.66,
                "GBPAUD": 80582.55,
                "GBPJPY": 79951.99,
                "GBPUSD": 80954.97,
                "USDCAD": 79748.06,
                "USDJPY": 80739.78,
                "USDCHF": 80872.02,
                "NZDUSD": 79600.43,
                "UK100.cash": 79740.67,
                "US100.cash": 80275.02,
                "XAUUSD": 81307.8,
                "XRPUSD": 80149.06,
            },
            "0EUEV5SO": {
                "AUDUSD": 9863.96,
                "AUDJPY": 10054.77,
                "AUS200.cash": 10000.44,
                "BTCUSD": 9998.18,
                "ETHUSD": 9995.51,
                "EURAUD": 10019.04,
                "EURGBP": 10013.09,
                "EURJPY": 9895.79,
                "EURUSD": 9845.14,
                "EU50.cash": 10000.53,
                "GBPAUD": 10078.9,
                "GBPJPY": 10001.28,
                "GBPUSD": 10225.24,
                "USDCAD": 9927.8,
                "USDJPY": 9983.86,
                "USDCHF": 10186.84,
                "NZDUSD": 9887.55,
                "UK100.cash": 9976.97,
                "US100.cash": 10011.5,
                "XAUUSD": 9940.44,
            },
            "46TGTINM": {
                "GER40.cash": 20050.46,
                "US500.cash": 19997.2,
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
