import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from quant_core.metrics.trade_metric import TradeMetric


class AccountGrowthAbsoluteOverTime(TradeMetric):
    __TITLE__ = "Account Balance Over Time"
    __SUBTITLE__ = "Shows cumulative balance from trades"

    def run(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()
        df["time"] = pd.to_datetime(df["time"])
        df = df.sort_values(by="time")

        df["net"] = df["profit"] + df["commission"] + df["swap"]

        # Get the actual starting balance
        df["initial_balance"] = 0.0
        initial_balances = df[df["type"] == 2].groupby("Account")["profit"].first().to_dict()

        # Set initial balance manually
        for account, balance in initial_balances.items():
            df.loc[df["Account"] == account, "initial_balance"] = balance

        # Fill forward the initial balance
        df["initial_balance"] = df.groupby("Account")["initial_balance"].transform("max")

        # Calculate cumulative P&L (excluding type 2 entries, i.e., initial balance)
        df["cumulative_net"] = df.where(df["type"] != 2).groupby("Account")["net"].cumsum().fillna(0.0)

        # Final absolute balance = initial + cumulative net
        df["absolute_balance"] = df["initial_balance"] + df["cumulative_net"]

        return df

    def to_chart(self, df: pd.DataFrame) -> go.Figure:
        result_df = self.run(df)

        fig = px.line(
            result_df,
            x="time",
            y="absolute_balance",
            color="Account",
            title=self.__TITLE__,
            labels={"absolute_balance": "Balance", "time": "Time"},
        )
        fig.update_traces(mode="lines+markers")

        return fig
