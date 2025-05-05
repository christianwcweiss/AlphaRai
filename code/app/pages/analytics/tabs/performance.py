import pandas as pd
from dash import dcc

from components.atoms.layout.layout import AlphaRow, AlphaCol
from components.charts.bar.bar_chart import BarChart
from components.charts.chart import ChartLayoutStyle, ChartMargin
from components.charts.line.line_chart import LineChart
from components.charts.hist.histogram_chart import HistogramChart

from quant_core.metrics.expectancy_over_time.absolute.expectancy import ExpectancyOverTimeAbsolute
from quant_core.metrics.expectancy_over_time.relative.expectancy import ExpectancyOverTimeRelative
from quant_core.metrics.sharpe_over_time.sharpe import SharpeRatioOverTime
from quant_core.metrics.sortino_over_time.sortino import SortinoRatioOverTime
from quant_core.metrics.risk_reward_over_time.rr_ratio import RiskRewardRatioOverTime
from quant_core.metrics.profit_factor_over_time.profit_factor import ProfitFactorOverTime
from quant_core.metrics.kelly_criterion_over_time.kelly import KellyCriterionPerAccount


def _render_expectancy_absolute_chart(df: pd.DataFrame, split_by_account: bool) -> AlphaCol:
    metric = ExpectancyOverTimeAbsolute()
    result = metric.calculate_grouped(df) if split_by_account else metric.calculate_ungrouped(df)
    return AlphaCol(
        dcc.Graph(
            figure=LineChart(
                data_frame=result,
                line_layout_style=ChartLayoutStyle(
                    title="Expectancy (Absolute)",
                    x_axis_title="Date",
                    y_axis_title="Expectancy",
                    show_legend=False,
                    margin=ChartMargin(30, 30, 30, 30),
                ),
            ).plot(x_col="time", y_col="expectancy", group_by="account_id" if split_by_account else None)
        ),
        xs=12, sm=12, md=12, lg=6, xl=6,
    )


def _render_expectancy_relative_chart(df: pd.DataFrame, split_by_account: bool) -> AlphaCol:
    metric = ExpectancyOverTimeRelative()
    result = metric.calculate_grouped(df) if split_by_account else metric.calculate_ungrouped(df)
    return AlphaCol(
        dcc.Graph(
            figure=LineChart(
                data_frame=result,
                line_layout_style=ChartLayoutStyle(
                    title="Expectancy (Relative)",
                    x_axis_title="Date",
                    y_axis_title="Expectancy (%)",
                    show_legend=False,
                    margin=ChartMargin(30, 30, 30, 30),
                ),
            ).plot(x_col="time", y_col="expectancy_pct", group_by="account_id" if split_by_account else None)
        ),
        xs=12, sm=12, md=12, lg=6, xl=6,
    )


def _render_profit_factor_chart(df: pd.DataFrame, split_by_account: bool) -> AlphaCol:
    metric = ProfitFactorOverTime()
    result = metric.calculate_grouped(df) if split_by_account else metric.calculate_ungrouped(df)
    return AlphaCol(
        dcc.Graph(
            figure=LineChart(
                data_frame=result,
                line_layout_style=ChartLayoutStyle(
                    title="Profit Factor",
                    x_axis_title="Date",
                    y_axis_title="Factor",
                    show_legend=False,
                    margin=ChartMargin(30, 30, 30, 30),
                ),
            ).plot(x_col="time", y_col="profit_factor", group_by="account_id" if split_by_account else None)
        ),
        xs=12, sm=12, md=12, lg=6, xl=6,
    )


def _render_risk_reward_chart(df: pd.DataFrame, split_by_account: bool) -> AlphaCol:
    metric = RiskRewardRatioOverTime()
    result = metric.calculate_grouped(df) if split_by_account else metric.calculate_ungrouped(df)
    return AlphaCol(
        dcc.Graph(
            figure=LineChart(
                data_frame=result,
                line_layout_style=ChartLayoutStyle(
                    title="Risk-Reward Ratio",
                    x_axis_title="Date",
                    y_axis_title="Ratio",
                    show_legend=False,
                    margin=ChartMargin(30, 30, 30, 30),
                    y_range=[-10, 10]
                ),
            ).plot(x_col="time", y_col="risk_reward", group_by="account_id" if split_by_account else None)
        ),
        xs=12, sm=12, md=12, lg=6, xl=6,
    )


def _render_sharpe_ratio_chart(df: pd.DataFrame, split_by_account: bool) -> AlphaCol:
    metric = SharpeRatioOverTime()
    result = metric.calculate_grouped(df) if split_by_account else metric.calculate_ungrouped(df)
    return AlphaCol(
        dcc.Graph(
            figure=LineChart(
                data_frame=result,
                line_layout_style=ChartLayoutStyle(
                    title="Sharpe Ratio",
                    x_axis_title="Date",
                    y_axis_title="Sharpe",
                    show_legend=False,
                    margin=ChartMargin(30, 30, 30, 30),
                ),
            ).plot(x_col="time", y_col="sharpe", group_by="account_id" if split_by_account else None)
        ),
        xs=12, sm=12, md=12, lg=6, xl=6,
    )


def _render_sortino_ratio_chart(df: pd.DataFrame, split_by_account: bool) -> AlphaCol:
    metric = SortinoRatioOverTime()
    result = metric.calculate_grouped(df) if split_by_account else metric.calculate_ungrouped(df)
    return AlphaCol(
        dcc.Graph(
            figure=LineChart(
                data_frame=result,
                line_layout_style=ChartLayoutStyle(
                    title="Sortino Ratio",
                    x_axis_title="Date",
                    y_axis_title="Sortino",
                    show_legend=False,
                    margin=ChartMargin(30, 30, 30, 30),
                    y_range=[-2, 2]
                ),
            ).plot(x_col="time", y_col="sortino", group_by="account_id" if split_by_account else None)
        ),
        xs=12, sm=12, md=12, lg=6, xl=6,
    )


def _render_kelly_per_account_chart(df: pd.DataFrame, split_by_account: bool) -> AlphaCol:
    metric = KellyCriterionPerAccount()
    result = metric.calculate(df)

    return AlphaCol(
        dcc.Graph(
            figure=BarChart(
                data_frame=result,
                bar_layout_style=ChartLayoutStyle(
                    title="Kelly Criterion per Account",
                    x_axis_title="Account",
                    y_axis_title="Kelly (%)",
                    margin=ChartMargin(30, 30, 30, 30),
                    y_range=[0, 100],
                    show_legend=False
                ),
            ).plot(x_col="account_id", y_col="kelly_pct")
        ),
        xs=12, sm=12, md=12, lg=12, xl=12,
    )


def render(data_frame: pd.DataFrame, split_by_account: bool = True) -> AlphaRow:
    return AlphaRow(
        children=[
            _render_expectancy_absolute_chart(data_frame, split_by_account),
            _render_expectancy_relative_chart(data_frame, split_by_account),
            _render_profit_factor_chart(data_frame, split_by_account),
            _render_risk_reward_chart(data_frame, split_by_account),
            _render_sharpe_ratio_chart(data_frame, split_by_account),
            _render_sortino_ratio_chart(data_frame, split_by_account),
            _render_kelly_per_account_chart(data_frame, split_by_account),
        ]
    )
