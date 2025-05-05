import pandas as pd
from quant_core.metrics.trade_metric import TradeMetricOverTime


class ProfitFactorOverTime(TradeMetricOverTime):
    def calculate_grouped(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()
        df["time"] = pd.to_datetime(df["time"])
        df = df[df["profit"].notna()]
        result = []

        for current_day, window_df in self.get_rolling_windows(df, skip_head=True).items():
            for account, group in window_df.groupby("account_id"):
                total_profit = group[group["profit"] > 0]["profit"].sum()
                total_loss = abs(group[group["profit"] < 0]["profit"].sum())

                pf = total_profit / total_loss if total_loss > 0 else 0.0
                result.append({
                    "time": current_day,
                    "account_id": account,
                    "profit_factor": round(pf, 2)
                })

        return pd.DataFrame(result)

    def calculate_ungrouped(self, df: pd.DataFrame) -> pd.DataFrame:
        grouped = self.calculate_grouped(df)
        return (
            grouped.groupby("time")["profit_factor"]
            .mean()
            .reset_index()
        )