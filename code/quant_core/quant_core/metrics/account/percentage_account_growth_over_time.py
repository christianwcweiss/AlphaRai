import pandas as pd
import plotly.graph_objects as go
from quant_core.metrics.trade_metric import TradeMetric
from quant_ui.charts.line_chart import LineChart


class AccountGrowthPercentageOverTime(TradeMetric):
    __TITLE__ = "Account Growth Percentage Over Time"
    __SUBTITLE__ = "Shows percentage growth of account balance from trades"

    def _run(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()
        df["time"] = pd.to_datetime(df["time"])
        df = df.sort_values(by="time")
        df["net"] = df["profit"] + df["commission"] + df["swap"]
        df["initial_balance"] = 0.0
        initial_balances = df[df["type"] == 2].groupby("Account")["profit"].first().to_dict()

        for account, balance in initial_balances.items():
            df.loc[df["Account"] == account, "initial_balance"] = balance

        df["initial_balance"] = df.groupby("Account")["initial_balance"].transform("max")
        df["cumulative_net"] = df.where(df["type"] != 2).groupby("Account")["net"].cumsum().fillna(0.0)
        df["absolute_balance"] = df["initial_balance"] + df["cumulative_net"]
        df["percentage_growth"] = ((df["absolute_balance"] - df["initial_balance"]) / df["initial_balance"]) * 100

        return df

    def to_chart(self, df: pd.DataFrame) -> go.Figure:
        result_df = self._run(df)
        fig = LineChart(title=self.__TITLE__, subtitle=self.__SUBTITLE__, show_legend=False).plot(
            data_frame=result_df,
            x_col="time",
            y_col=["percentage_growth"],
            groupby="Account",
        )
        return fig
