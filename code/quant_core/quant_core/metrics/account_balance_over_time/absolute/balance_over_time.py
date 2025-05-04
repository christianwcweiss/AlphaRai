import pandas as pd

from quant_core.metrics.trade_metric import TradeMetric


class AccountBalanceOverTimeAbsolute(TradeMetric):
    def calculate(self, data_frame: pd.DataFrame) -> pd.DataFrame:
        data_frame = data_frame.copy()
        data_frame["time"] = pd.to_datetime(data_frame["time"])
        data_frame = data_frame.sort_values(by="time")

        data_frame["net"] = data_frame["profit"] + data_frame["commission"] + data_frame["swap"]

        data_frame["initial_balance"] = 0.0
        initial_balances = data_frame[data_frame["type"] == 2].groupby("account_id")["profit"].first().to_dict()

        for account, balance in initial_balances.items():
            data_frame.loc[data_frame["account_id"] == account, "initial_balance"] = balance

        data_frame["initial_balance"] = data_frame.groupby("account_id")["initial_balance"].transform("max")
        data_frame["cumulative_net"] = (
            data_frame.where(data_frame["type"] != 2).groupby("account_id")["net"].cumsum().fillna(0.0)
        )
        data_frame["absolute_balance"] = data_frame["initial_balance"] + data_frame["cumulative_net"]

        return data_frame
