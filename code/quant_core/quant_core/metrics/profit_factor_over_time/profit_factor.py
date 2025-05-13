import pandas as pd
from quant_core.metrics.trade_metric_over_time import TradeMetricOverTime


class ProfitFactorOverTime(TradeMetricOverTime):
    """Calculates the profit factor over time."""

    def calculate(
        self,
        data_frame: pd.DataFrame,
        group_by_account_id: bool = True,
        group_by_symbol: bool = False,
        group_by_hour: bool = False,
        group_by_day: bool = False,
        rolling_window: int = 30,
    ) -> pd.DataFrame:
        data_frame = data_frame.copy()
        data_frame["time"] = pd.to_datetime(data_frame["time"])

        result = []

        for current_day, window_df in self.get_rolling_windows(data_frame, skip_head=True).items():
            for account, group in window_df.groupby("account_id"):
                total_profit = group[group["profit"] > 0]["profit"].sum()
                total_loss = abs(group[group["profit"] < 0]["profit"].sum())

                pf = total_profit / total_loss if total_loss > 0 else 0.0
                result.append({"time": current_day, "account_id": account, "profit_factor": round(pf, 2)})

        return pd.DataFrame(result)
