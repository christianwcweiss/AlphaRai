from typing import Optional, Literal
from itertools import product

import pandas as pd
from quant_core.metrics.trade_metric_over_time import TradeMetricOverTime


class FeesOverTime(TradeMetricOverTime):
    """Calculates the total commission over time."""

    def _calculate_comission_in_cum_sum(
        self,
        data_frame: pd.DataFrame,
        group_by_account_id: bool = False,
        group_by_symbol: bool = False,
    ) -> pd.DataFrame:
        groups = self.groups(group_by_account_id=group_by_account_id, group_by_symbol=group_by_symbol)

        if groups:
            data_frame["total_commission"] = data_frame.groupby(groups)["commission"].cumsum()
            data_frame["total_swap"] = data_frame.groupby(groups)["swap"].cumsum()
            data_frame["total_fees"] = data_frame["total_commission"] + data_frame["total_swap"]
        else:
            data_frame["total_commission"] = data_frame["commission"].cumsum()
            data_frame["total_swap"] = data_frame["swap"].cumsum()
            data_frame["total_fees"] = data_frame["total_commission"] + data_frame["total_swap"]

        data_frame = data_frame.drop_duplicates(keep="last")

        return data_frame[["closed_at"] + groups + ["total_commission", "total_swap", "total_fees"]]

    def _calculate_commission_in_period_windows(
        self,
        data_frame: pd.DataFrame,
        group_by_account_id: bool = False,
        group_by_symbol: bool = False,
        rolling_window: Optional[int] = 7,
        aggregation_resolution: Literal["D", "H"] = "D",
    ) -> pd.DataFrame:
        rolling_windows = self.get_rolling_windows(
            data_frame=data_frame,
            skip_head=False,
            aggregation_resolution=aggregation_resolution,
            rolling_window=rolling_window if rolling_window else None,
        )

        groups = self.groups(group_by_account_id=group_by_account_id, group_by_symbol=group_by_symbol)
        result = []

        group_values = {group: data_frame[group].dropna().unique() for group in groups}

        for window_time, window_df in rolling_windows.items():
            if not window_df.empty:
                if groups:
                    window_df["total_commission"] = window_df.groupby(groups)["commission"].transform("sum")
                    window_df["total_swap"] = window_df.groupby(groups)["swap"].transform("sum")
                    window_df["total_fees"] = window_df["total_commission"] + window_df["total_swap"]
                else:
                    window_df["total_commission"] = window_df["commission"].sum()
                    window_df["total_swap"] = window_df["swap"].sum()
                    window_df["total_fees"] = window_df["total_commission"] + window_df["total_swap"]

                window_df["closed_at"] = window_time
                window_df = window_df.drop_duplicates(subset=groups + ["closed_at"], keep="last")
                result.extend(window_df.to_dict("records"))

            if groups:
                all_combos = list(product(*(group_values[g] for g in groups)))
                expected_rows = pd.DataFrame(
                    [
                        dict(zip(groups, combo))
                        | {"closed_at": window_time, "total_commission": 0.0, "total_swap": 0.0, "total_fees": 0.0}
                        for combo in all_combos
                    ]
                )
            else:
                expected_rows = pd.DataFrame(
                    [
                        {
                            "closed_at": window_time,
                            "total_commission": 0.0,
                            "total_swap": 0.0,
                            "total_fees": 0.0,
                            **{col: pd.NA for col in groups},
                        }
                    ]
                )

            for group_col in groups:
                expected_dtype = data_frame[group_col].dtype
                expected_rows[group_col] = expected_rows[group_col].astype(expected_dtype)

            result_df_temp = pd.DataFrame(result)
            merge_keys = ["closed_at"] + groups
            existing_rows = result_df_temp[merge_keys] if not result_df_temp.empty else pd.DataFrame(columns=merge_keys)
            existing_rows = existing_rows.dropna(subset=merge_keys)

            missing = expected_rows.merge(existing_rows, how="left", on=merge_keys, indicator=True)
            missing = missing[missing["_merge"] == "left_only"].drop(columns="_merge")

            if not missing.empty:
                result.extend(missing.to_dict("records"))

        result_df = pd.DataFrame(result)
        return result_df[["closed_at"] + groups + ["total_commission", "total_swap", "total_fees"]]

    def calculate(  # pylint: disable=too-many-arguments, too-many-positional-arguments
        self,
        data_frame: pd.DataFrame,
        group_by_account_id: bool = False,
        group_by_symbol: bool = False,
        rolling_window: Optional[int] = 7,
        aggregation_resolution: Literal["D", "H"] = "D",
        cum_sum: bool = False,
    ) -> pd.DataFrame:
        commission_df = self._normalize_time(data_frame)

        if cum_sum:
            result_df = self._calculate_comission_in_cum_sum(
                data_frame=commission_df,
                group_by_account_id=group_by_account_id,
                group_by_symbol=group_by_symbol,
            )
        else:
            result_df = self._calculate_commission_in_period_windows(
                data_frame=commission_df,
                group_by_account_id=group_by_account_id,
                group_by_symbol=group_by_symbol,
                rolling_window=rolling_window,
                aggregation_resolution=aggregation_resolution,
            )

        return result_df
