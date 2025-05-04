import pandas as pd

from quant_core.metrics.trade_metric import TradeMetric


class ProfitPerSymbolOverTimeRelative(TradeMetric):
    def calculate(self, data_frame: pd.DataFrame) -> pd.DataFrame:
        if data_frame.empty or "symbol" not in data_frame.columns or "profit" not in data_frame.columns:
            return pd.DataFrame(columns=["time", "symbol", "profit_pct"])

        df = data_frame.copy()
        df["time"] = pd.to_datetime(df["time"]).dt.date

        # Sum profit per time and symbol
        grouped = df.groupby(["time", "symbol"])["profit"].sum().reset_index()

        # Total profit per day (to normalize)
        total_by_day = grouped.groupby("time")["profit"].sum().reset_index()
        total_by_day.columns = ["time", "total_profit"]

        # Merge total into grouped
        result = pd.merge(grouped, total_by_day, on="time")
        result["profit_pct"] = result.apply(
            lambda row: (row["profit"] / row["total_profit"] * 100) if row["total_profit"] != 0 else 0.0,
            axis=1
        )

        return result[["time", "symbol", "profit_pct"]].sort_values("time")