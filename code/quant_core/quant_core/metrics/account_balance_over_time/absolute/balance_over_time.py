import pandas as pd
from quant_core.metrics.trade_metric import TradeMetricOverTime


class AccountBalanceOverTimeAbsolute(TradeMetricOverTime):
    def calculate_grouped(self, data_frame: pd.DataFrame) -> pd.DataFrame:
        df = data_frame.copy()
        df["time"] = pd.to_datetime(df["time"])
        df = df.sort_values("time")

        df["net"] = df["profit"] + df["commission"] + df["swap"]

        df["initial_balance"] = 0.0
        initial_balances = self._get_initial_balances(df)
        for account, balance in initial_balances.items():
            df.loc[df["account_id"] == account, "initial_balance"] = balance

        df["initial_balance"] = df.groupby("account_id")["initial_balance"].transform("max")

        df["cumulative_net"] = df.where(df["type"] != 2).groupby("account_id")["net"].cumsum().fillna(0.0)

        df["absolute_balance"] = df["initial_balance"] + df["cumulative_net"]

        return df[["time", "account_id", "absolute_balance"]]

    def calculate_ungrouped(self, data_frame: pd.DataFrame) -> pd.DataFrame:
        grouped = self.calculate_grouped(data_frame)

        return grouped.groupby("time")["absolute_balance"].agg("mean").mean().reset_index()
