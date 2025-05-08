import pandas as pd
from dash import dcc

from components.atoms.layout.layout import AlphaRow, AlphaCol
from components.charts.bar.bar_chart import BarChart
from components.charts.chart import ChartLayoutStyle, ChartMargin
from components.charts.line.line_chart import LineChart
from components.charts.heatmap.heatmap_chart import HeatmapChart
from quant_core.metrics.average_hold_time_over_time.trade_duration import AvgHoldTimeOverTime
from quant_core.metrics.average_trade_duration_over_time.trade_duration import AvgTradeDurationOverTime
from quant_core.metrics.profit_loss_by_hour_over_time.profit_loss import ProfitByHourOverTime
from quant_core.metrics.profit_loss_by_weekday_over_time.profit_loss import ProfitByWeekdayOverTime
from quant_core.metrics.trades_per_day.trades_per_day import TradesPerDay
from quant_core.metrics.win_rate_over_time.win_rate_over_time import WinRateOverTime


def _render_win_rate_chart(df: pd.DataFrame, split_by_account: bool) -> AlphaCol:
    metric = WinRateOverTime()
    result = metric.calculate_grouped(df) if split_by_account else metric.calculate_ungrouped(df)

    return AlphaCol(
        dcc.Graph(
            figure=LineChart(
                data_frame=result,
                line_layout_style=ChartLayoutStyle(
                    title="Win Rate Over Time",
                    x_axis_title="Date",
                    y_axis_title="Win Rate (%)",
                    show_legend=split_by_account,
                    margin=ChartMargin(30, 30, 30, 30),
                    y_range=[0, 100],
                ),
            ).plot(x_col="time", y_col="win_rate", group_by="account_id" if split_by_account else None)
        ),
        xs=12,
        sm=12,
        md=12,
        lg=6,
        xl=6,
    )


def _render_avg_trade_duration_chart(df: pd.DataFrame) -> AlphaCol:
    metric = AvgTradeDurationOverTime()
    result = metric.calculate_grouped(df)  # expected output: columns = ["time", "win_duration", "loss_duration"]

    return AlphaCol(
        dcc.Graph(
            figure=BarChart(
                data_frame=result,
                bar_layout_style=ChartLayoutStyle(
                    title="Average Trade Duration (Win vs. Loss)",
                    x_axis_title="Date",
                    y_axis_title="Duration (minutes)",
                    margin=ChartMargin(30, 30, 30, 30),
                    show_legend=True,
                ),
            ).plot(x_col="time", y_col="avg_duration_min")
        ),
        xs=12,
        sm=12,
        md=12,
        lg=12,
        xl=12,
    )


def _render_avg_hold_time_chart(df: pd.DataFrame, split_by_account: bool) -> AlphaCol:
    metric = AvgHoldTimeOverTime()
    result = metric.calculate_grouped(df) if split_by_account else metric.calculate_ungrouped(df)

    return AlphaCol(
        dcc.Graph(
            figure=LineChart(
                data_frame=result,
                line_layout_style=ChartLayoutStyle(
                    title="Average Hold Time Over Time",
                    x_axis_title="Date",
                    y_axis_title="Hold Time (minutes)",
                    show_legend=split_by_account,
                    margin=ChartMargin(30, 30, 30, 30),
                ),
            ).plot(x_col="time", y_col="hold_time", group_by="account_id" if split_by_account else None)
        ),
        xs=12,
        sm=12,
        md=12,
        lg=6,
        xl=6,
    )


def _render_trades_per_day_chart(df: pd.DataFrame, split_by_account: bool) -> AlphaCol:
    metric = TradesPerDay()
    result = metric.calculate_grouped(df) if split_by_account else metric.calculate_ungrouped(df)

    return AlphaCol(
        dcc.Graph(
            figure=LineChart(
                data_frame=result,
                line_layout_style=ChartLayoutStyle(
                    title="Trades Per Day",
                    x_axis_title="Date",
                    y_axis_title="Number of Trades",
                    show_legend=split_by_account,
                    margin=ChartMargin(30, 30, 30, 30),
                ),
            ).plot(x_col="time", y_col="trade_count", group_by="account_id" if split_by_account else None)
        ),
        xs=12,
        sm=12,
        md=12,
        lg=6,
        xl=6,
    )


def _render_profit_by_hour_chart(df: pd.DataFrame) -> AlphaCol:
    metric = ProfitByHourOverTime()
    result = metric.calculate_grouped(df)

    return AlphaCol(
        dcc.Graph(
            figure=HeatmapChart(
                data_frame=result,
                layout_style=ChartLayoutStyle(
                    title="Profit by Hour",
                    x_axis_title="Hour of Day",
                    y_axis_title="Account",
                    margin=ChartMargin(30, 30, 30, 30),
                    show_legend=False,
                ),
            ).plot(x_col="hour", y_col="account_id", value_col="profit")
        ),
        xs=12,
        sm=12,
        md=12,
        lg=12,
        xl=12,
    )


def _render_profit_by_weekday_chart(df: pd.DataFrame) -> AlphaCol:
    metric = ProfitByWeekdayOverTime()
    result = metric.calculate_grouped(df)  # columns: weekday, profit (avg)

    return AlphaCol(
        dcc.Graph(
            figure=BarChart(
                data_frame=result,
                bar_layout_style=ChartLayoutStyle(
                    title="Profit by Weekday",
                    x_axis_title="Weekday",
                    y_axis_title="Average Profit",
                    margin=ChartMargin(30, 30, 30, 30),
                    show_legend=False,
                ),
            ).plot(x_col="weekday", y_col="avg_profit")
        ),
        xs=12,
        sm=12,
        md=12,
        lg=12,
        xl=12,
    )


def render(data_frame: pd.DataFrame, split_by_account: bool = True) -> AlphaRow:
    return AlphaRow(
        children=[
            _render_win_rate_chart(data_frame, split_by_account),
            _render_avg_trade_duration_chart(data_frame),
            _render_avg_hold_time_chart(data_frame, split_by_account),
            _render_trades_per_day_chart(data_frame, split_by_account),
            _render_profit_by_hour_chart(data_frame),
            _render_profit_by_weekday_chart(data_frame),
        ]
    )
