import pandas as pd
import plotly.graph_objects as go

from components.atoms.charts.line.line_chart import LineChart
from quant_core.metrics.trade_metric import TradeMetric


class AccountGrowthPercentageOverTime(TradeMetric):
    def calculate(self, data_frame: pd.DataFrame) -> pd.DataFrame:
        data_frame = data_frame.copy()
        data_frame["time"] = pd.to_datetime(data_frame["time"])
        data_frame = data_frame.sort_values(by="time")
        data_frame["net"] = data_frame["profit"] + data_frame["commission"] + data_frame["swap"]
        data_frame["initial_balance"] = 0.0
        initial_balances = data_frame[data_frame["type"] == 2].groupby("Account")["profit"].first().to_dict()

        for account, balance in initial_balances.items():
            data_frame.loc[data_frame["Account"] == account, "initial_balance"] = balance

        data_frame["initial_balance"] = data_frame.groupby("Account")["initial_balance"].transform("max")
        data_frame["cumulative_net"] = (
            data_frame.where(data_frame["type"] != 2).groupby("Account")["net"].cumsum().fillna(0.0)
        )
        data_frame["absolute_balance"] = data_frame["initial_balance"] + data_frame["cumulative_net"]
        data_frame["percentage_growth"] = (
            (data_frame["absolute_balance"] - data_frame["initial_balance"]) / data_frame["initial_balance"]
        ) * 100

        return data_frame
