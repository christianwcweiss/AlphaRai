import dash
import pandas as pd
import dash_bootstrap_components as dbc
from dash import html, dcc, Input, Output, callback

from components.atoms.tabbar.tabbar import AlphaTabToolbar
from components.atoms.text.page import PageHeader
from components.atoms.content import MainContent
from components.frame.body import PageBody
from components.atoms.layout.layout import AlphaRow, AlphaCol
from db.database import SessionLocal
from models.account import Account
from pages.analytics.analysis import TAB_LABELS
from pages.base_page import BasePage
from quant_core.enums.platform import Platform
from services.db.trade_history import get_all_trades

from quant_core.metrics.expectancy_over_time.absolute.expectancy import ExpectancyOverTimeAbsolute
from quant_core.metrics.expectancy_over_time.relative.expectancy import ExpectancyOverTimeRelative
from quant_core.metrics.sharpe_over_time.sharpe import SharpeRatioOverTime
from quant_core.metrics.sortino_over_time.sortino import SortinoRatioOverTime
from quant_core.metrics.risk_reward_over_time.rr_ratio import RiskRewardRatioOverTime
from quant_core.metrics.profit_factor_over_time.profit_factor import ProfitFactorOverTime
from quant_core.metrics.kelly_criterion_over_time.kelly import KellyCriterionPerAccount
from components.charts.bar.bar_chart import BarChart
from components.charts.chart import ChartLayoutStyle, ChartMargin
from components.charts.line.line_chart import LineChart
from components.molecules.charts.expectancy_over_time.expectancy_over_time import ExpectancyOverTime


dash.register_page(__name__, path="/analysis/performance", name="Performance")


def _render_account_dropdown() -> dcc.Dropdown:
    with SessionLocal() as session:
        accounts = session.query(Account).filter_by(platform=Platform.METATRADER.value, enabled=True).all()

    return dcc.Dropdown(
        id="account-dropdown",
        options=[{"label": "All Accounts", "value": "ALL"}] +
                [{"label": a.uid, "value": a.uid} for a in accounts],
        value="ALL",
        clearable=False,
        style={"width": "300px", "marginBottom": "20px"},
    )


def _render_chart(metric, df: pd.DataFrame, y_col: str, title: str, y_axis_title: str, y_range=None, split_by_account=True) -> AlphaCol:
    result = metric.calculate_grouped(df) if split_by_account else metric.calculate_ungrouped(df)
    return AlphaCol(
        dcc.Graph(
            figure=LineChart(
                data_frame=result,
                line_layout_style=ChartLayoutStyle(
                    title=title,
                    x_axis_title="Date",
                    y_axis_title=y_axis_title,
                    show_legend=False,
                    margin=ChartMargin(30, 30, 30, 30),
                    y_range=y_range
                ),
            ).plot(x_col="time", y_col=y_col, group_by="account_id" if split_by_account else None)
        ),
        xs=12, sm=12, md=12, lg=6, xl=6,
    )


def _render_kelly_chart(df: pd.DataFrame) -> AlphaCol:
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


class PerformancePage(BasePage):
    def render(self):
        return PageBody([
            PageHeader(self._title).render(),
            MainContent([
                AlphaTabToolbar(
                    tab_labels=TAB_LABELS,
                    base_href="/analysis",
                    current_tab="performance",
                    link_with_hash=False
                ).render(),
                _render_account_dropdown(),
                dcc.Loading(html.Div(id="performance-content")),
            ])
        ])


layout = PerformancePage("Performance").layout


@callback(
    Output("performance-content", "children"),
    Input("account-dropdown", "value"),
)
def render_performance_tab(selected_account):
    trades = get_all_trades()
    if not trades:
        return dbc.Alert("⚠️ No trade data found.", color="warning")

    df = pd.DataFrame([t.__dict__ for t in trades])
    df = df[[col for col in df.columns if not col.startswith("_sa_")]]

    if selected_account != "ALL":
        df = df[df["account_id"] == selected_account]

    if df.empty:
        return dbc.Alert("⚠️ No trade data available for the selected account.", color="warning")

    abs_df = ExpectancyOverTimeAbsolute().calculate_grouped(df)
    rel_df = ExpectancyOverTimeRelative().calculate_grouped(df)

    return AlphaRow([
        AlphaCol(
            ExpectancyOverTime(abs_df, rel_df).render(),
            xs=12, sm=12, md=12, lg=6, xl=6,
        ),
        # _render_chart(ProfitFactorOverTime(), df, "profit_factor", "Profit Factor", "Factor"),
        # _render_chart(RiskRewardRatioOverTime(), df, "risk_reward", "Risk-Reward Ratio", "Ratio", y_range=[-10, 10]),
        # _render_chart(SharpeRatioOverTime(), df, "sharpe", "Sharpe Ratio", "Sharpe"),
        # _render_chart(SortinoRatioOverTime(), df, "sortino", "Sortino Ratio", "Sortino", y_range=[-2, 2]),
        # _render_kelly_chart(df),
    ])
