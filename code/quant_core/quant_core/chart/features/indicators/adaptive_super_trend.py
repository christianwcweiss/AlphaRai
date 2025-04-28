from typing import List

import numpy as np
import pandas as pd
from sklearn.cluster import KMeans

from quant_core.chart.feature import DataFeature
from quant_core.chart.features.indicators.average_true_range import DataFeatureAverageTrueRange
from quant_core.utils.chart_utils import check_df_sorted, check_enough_rows


class DataFeatureAdaptiveSuperTrend(DataFeature):
    def __init__(
        self,
        atr_period: int = 10,
        min_factor: float = 1.0,
        max_factor: float = 5.0,
        step: float = 0.5,
        perf_alpha: float = 10.0,
        from_cluster: str = "Best",
        max_iter: int = 1000,
        max_data: int = 10000,
    ) -> None:
        self._atr_period = atr_period
        self._min_factor = min_factor
        self._max_factor = max_factor
        self._step = step
        self._perf_alpha = perf_alpha
        self._from_cluster = from_cluster
        self._max_iter = max_iter
        self._max_data = max_data

    def get_columns(self) -> List[str]:
        common_params = [
            str(self._atr_period),
            str(self._min_factor),
            str(self._max_factor),
            str(self._step),
            str(self._perf_alpha),
            str(self._from_cluster),
        ]

        adapt_super_trend_column = "_".join(["ada_st"] + common_params)
        adapt_direction_column = "_".join(["ada_dir"] + common_params)
        atr_cluster_column = "_".join(["atr_clu"] + common_params)
        lv_new_column = "_".join(["lv"] + common_params)
        mv_new_column = "_".join(["mv"] + common_params)
        hv_new_column = "_".join(["hv"] + common_params)

        return [
            adapt_super_trend_column,
            adapt_direction_column,
            atr_cluster_column,
            lv_new_column,
            mv_new_column,
            hv_new_column,
        ]

    def add_feature(self, data_frame: pd.DataFrame) -> pd.DataFrame:
        (
            adapt_super_trend_column,
            adapt_direction_column,
            chosen_factor_column,
            lv_new_column,
            mv_new_column,
            hv_new_column,
        ) = self.get_columns()
        if all(
            col in data_frame.columns
            for col in {
                adapt_super_trend_column,
                adapt_direction_column,
                chosen_factor_column,
                lv_new_column,
                mv_new_column,
                hv_new_column,
            }
        ):
            return data_frame

        check_df_sorted(data_frame=data_frame)
        check_enough_rows(data_frame=data_frame)

        df = data_frame.copy()

        # 1) ATR Calculation
        # Using your existing "DataFeatureAverageTrueRange" => just be mindful that
        # it's likely an EMA, not Wilder's. If you want to match Pine exactly, implement Wilder's.
        atr_feat = DataFeatureAverageTrueRange(self._atr_period)
        atr_name = atr_feat.get_columns()[0]
        df = atr_feat.add_feature(df)

        df["_hl2_"] = 0.5 * (df["high"] + df["low"])

        # 2) Build factor list
        factor_values = []
        v = self._min_factor
        while v <= self._max_factor + 1e-9:
            factor_values.append(round(v, 5))
            v += self._step

        if not factor_values:
            # No valid factors => just return
            return data_frame

        # We'll only do the multi-factor "performance" pass on the last max_data bars.
        df_factors = df.tail(self._max_data).copy()
        df_factors.dropna(subset=[atr_name, "_hl2_", "close"], inplace=True)

        # Container for each factor's running state
        class SuperTrendState:
            __slots__ = ("upper", "lower", "trend", "output", "perf")

            def __init__(self):
                self.upper = np.nan
                self.lower = np.nan
                self.trend = 0
                self.output = np.nan
                self.perf = 0.0

        st_list = [SuperTrendState() for _ in factor_values]

        # Pine uses alpha = 2/(perfAlpha+1)
        alpha = 2.0 / (self._perf_alpha + 1.0)

        # 3) Multi-factor pass to measure performance
        # The script references close[1] in places => handle with i-1 carefully
        for i in range(len(df_factors)):
            c = df_factors["close"].iloc[i]
            c1 = df_factors["close"].iloc[i - 1] if i > 0 else c
            hl2_ = df_factors["_hl2_"].iloc[i]
            atr_ = df_factors[atr_name].iloc[i]

            if np.isnan(atr_):
                continue

            for st_state, factor in zip(st_list, factor_values):
                # up/dn for this bar
                up_ = hl2_ + factor * atr_
                dn_ = hl2_ - factor * atr_

                if i == 0:
                    # init
                    st_state.upper = up_
                    st_state.lower = dn_
                    # trend
                    if c > st_state.upper:
                        st_state.trend = 1
                    elif c < st_state.lower:
                        st_state.trend = 0
                    # output
                    st_state.output = st_state.lower if st_state.trend == 1 else st_state.upper
                    # performance init
                    st_state.perf = 0.0
                else:
                    # *Compare the PREVIOUS bar's close to the PREVIOUS bar's upper/lower*
                    prev_close = c1
                    prev_upper = st_state.upper
                    prev_lower = st_state.lower
                    prev_output = st_state.output

                    # Update upper
                    if prev_close < prev_upper:
                        st_state.upper = min(up_, prev_upper)
                    else:
                        st_state.upper = up_
                    # Update lower
                    if prev_close > prev_lower:
                        st_state.lower = max(dn_, prev_lower)
                    else:
                        st_state.lower = dn_

                    # Update trend => using the CURRENT bar's close
                    # Pine: close > upper => 1, close < lower => 0
                    if c > st_state.upper:
                        st_state.trend = 1
                    elif c < st_state.lower:
                        st_state.trend = 0
                    # else remain the same

                    # Perf update => diff = sign(close[1] - output_previous)
                    diff = np.sign(c1 - prev_output)
                    st_state.perf += alpha * ((c - c1) * diff - st_state.perf)

                    # Final output => if trend=1 => lower, else upper
                    if st_state.trend == 1:
                        st_state.output = st_state.lower
                    else:
                        st_state.output = st_state.upper

        # 4) K-Means => cluster final performances
        final_perfs = np.array([s.perf for s in st_list]).reshape(-1, 1)

        km = KMeans(n_clusters=3, n_init=10, max_iter=self._max_iter, random_state=42)
        labels = km.fit_predict(final_perfs)
        centroids = km.cluster_centers_.flatten()

        # Sort ascending => worst=0, average=1, best=2
        sorted_idx = np.argsort(centroids)
        cluster_rank = {}
        for rank, cid in enumerate(sorted_idx):
            cluster_rank[cid] = rank

        # Map each label => [0,1,2]
        factor_ranks = np.array([cluster_rank[label] for label in labels])

        pick_map = {"Worst": 0, "Average": 1, "Best": 2}
        chosen_rank = pick_map.get(self._from_cluster, 2)
        chosen_mask = factor_ranks == chosen_rank
        chosen_factors = np.array(factor_values)[chosen_mask]

        if len(chosen_factors) == 0:
            # fallback logic
            if chosen_rank == 2:
                # pick factor with highest perf
                best_idx = np.argmax(final_perfs)
                chosen_factor = factor_values[best_idx]
            elif chosen_rank == 0:
                # pick factor with lowest perf
                worst_idx = np.argmin(final_perfs)
                chosen_factor = factor_values[worst_idx]
            else:
                # pick the overall average
                chosen_factor = float(np.mean(factor_values))
        else:
            # pick the average factor in that cluster
            chosen_factor = chosen_factors.mean()

        # Sort out the centroids so we can store them
        worst_center = centroids[sorted_idx[0]]
        avg_center = centroids[sorted_idx[1]]
        best_center = centroids[sorted_idx[2]]

        # 5) Final performance index => perf_idx
        # Pine does:
        #  perf_idx = max(avgPerf,0) / den
        #  den=ta.ema(abs(close-close[1]),perfAlpha)
        df["_abs_chg_"] = (df["close"] - df["close"].shift(1)).abs()
        den_series = df["_abs_chg_"].ewm(span=int(self._perf_alpha), min_periods=1).mean()
        cluster_perf_vals = final_perfs[factor_ranks == chosen_rank]
        avg_perf = cluster_perf_vals.mean() if len(cluster_perf_vals) else 0.0
        if avg_perf < 0:
            avg_perf = 0
        final_den = den_series.iloc[-1] if len(den_series) else 1e-9
        if final_den == 0:
            final_den = 1e-9
        perf_idx = avg_perf / final_den

        # 6) Final pass => chosen_factor supertrend + AMA
        n = len(df)
        st_arr = np.full(n, np.nan)
        os_arr = np.full(n, 0, dtype=int)
        upper = np.full(n, np.nan)
        lower = np.full(n, np.nan)
        perf_ama = np.full(n, np.nan)

        for i in range(n):
            c = df["close"].iloc[i]
            c1 = df["close"].iloc[i - 1] if i > 0 else c
            hl2_ = df["_hl2_"].iloc[i]
            atr_ = df[atr_name].iloc[i]

            if np.isnan(hl2_) or np.isnan(atr_):
                continue

            up_ = hl2_ + chosen_factor * atr_
            dn_ = hl2_ - chosen_factor * atr_

            if i == 0:
                upper[i] = up_
                lower[i] = dn_
                # os => 1 if c>up else 0 if c<dn else remain
                if c > up_:
                    os_arr[i] = 1
                elif c < dn_:
                    os_arr[i] = 0
                st_arr[i] = lower[i] if os_arr[i] == 1 else upper[i]
                perf_ama[i] = st_arr[i]
            else:
                prev_close = c1
                upper_prev = upper[i - 1]
                lower_prev = lower[i - 1]
                os_prev = os_arr[i - 1]

                # upper[i]
                if prev_close < upper_prev:
                    upper[i] = min(up_, upper_prev)
                else:
                    upper[i] = up_

                # lower[i]
                if prev_close > lower_prev:
                    lower[i] = max(dn_, lower_prev)
                else:
                    lower[i] = dn_

                # os => 1 if c>upper[i], 0 if c<lower[i], else old
                if c > upper[i]:
                    os_arr[i] = 1
                elif c < lower[i]:
                    os_arr[i] = 0
                else:
                    os_arr[i] = os_prev

                st_arr[i] = lower[i] if os_arr[i] == 1 else upper[i]

                # AMA => perf_ama[i] = perf_ama[i-1] + perf_idx*(st_arr[i] - perf_ama[i-1])
                perf_ama[i] = perf_ama[i - 1] + perf_idx * (st_arr[i] - perf_ama[i - 1])

        # 7) Save to DataFrame
        df[adapt_super_trend_column] = st_arr
        df[adapt_direction_column] = os_arr
        df[chosen_factor_column] = chosen_factor
        df[lv_new_column] = worst_center
        df[mv_new_column] = avg_center
        df[hv_new_column] = best_center

        # Cleanup
        df.drop(columns=["_hl2_", "_abs_chg_", atr_name], inplace=True, errors="ignore")

        # Join back to original data_frame
        data_frame = data_frame.join(
            df[
                [
                    adapt_super_trend_column,
                    adapt_direction_column,
                    chosen_factor_column,
                    lv_new_column,
                    mv_new_column,
                    hv_new_column,
                ]
            ],
            how="left",
        )
        return data_frame

    def normalize_feature(self, data_frame: pd.DataFrame) -> pd.DataFrame:
        indicator_column_name = self.get_columns()[0]
        normalized_column_name = self.get_feature_columns()[0]

        data_frame[normalized_column_name] = (data_frame["close"] - data_frame[indicator_column_name]) / data_frame[
            "close"
        ]

        return data_frame

    def get_feature_columns(self) -> List[str]:
        return [self.get_columns()[0] + "_normalized"]
