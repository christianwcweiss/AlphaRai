import pandas as pd

from quant_core.metrics.trade_metric import TradeMetric


class WinRateOverTime(TradeMetric):
    def calculate(self, data_frame: pd.DataFrame) -> pd.DataFrame:
        if data_frame.empty:
            return pd.DataFrame(columns=["date", "win_rate"])

        data_frame = data_frame.copy()
        data_frame["date"] = data_frame["time"].dt.date
        data_frame["is_win"] = data_frame["profit"] > 0

        grouped = data_frame.groupby("date")["is_win"]
        win_rate_df = grouped.mean().reset_index()
        win_rate_df.rename(columns={"is_win": "win_rate"}, inplace=True)
        win_rate_df["win_rate"] = (win_rate_df["win_rate"] * 100).round(2)

        return win_rate_df