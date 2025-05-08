import pandas as pd
from quant_core.metrics.trade_metric import TradeMetricOverTime


class WinRateOverTime(TradeMetricOverTime):
    def calculate_grouped(self, data_frame: pd.DataFrame) -> pd.DataFrame:
        data_frame = data_frame.copy()
        data_frame["time"] = pd.to_datetime(data_frame["time"])
        data_frame = data_frame[data_frame["profit"].notna()]
        result = []

        for current_day, window_df in self.get_rolling_windows(data_frame, skip_head=True).items():
            for account, group in window_df.groupby("account_id"):
                if group.empty:
                    continue

                win_rate = (group["profit"] > 0).mean() * 100
                result.append(
                    {
                        "time": current_day,
                        "account_id": account,
                        "win_rate": round(win_rate, 2),
                    }
                )

        return pd.DataFrame(result)

    def calculate_ungrouped(self, data_frame: pd.DataFrame) -> pd.DataFrame:
        grouped = self.calculate_grouped(data_frame)
        return grouped.groupby("time")["win_rate"].mean().reset_index()
