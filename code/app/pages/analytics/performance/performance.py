import dash
import dash_bootstrap_components as dbc
import pandas as pd
from dash import html, dcc, Input, Output, callback

from components.atoms.content import MainContent
from components.atoms.layout.layout import AlphaRow, AlphaCol
from components.atoms.tabbar.tabbar import AlphaTabToolbar
from components.atoms.text.page import PageHeader
from components.charts.chart import ChartLayoutStyle, ChartMargin
from components.charts.line.line_chart import LineChart
from components.frame.body import PageBody
from components.molecules.charts.expectancy_over_time.expectancy_over_time import ExpectancyOverTimeMolecule
from db.database import MainSessionLocal
from models.main.account import Account
from pages.analytics.analysis import TAB_LABELS
from pages.base_page import BasePage
from quant_core.enums.platform import Platform
from quant_core.metrics.expectancy_over_time.expectancy_over_time import ExpectancyOverTime
from services.db.cache.trade_history import get_all_trades

dash.register_page(__name__, path="/analytics/performance", name="Performance")


def _render_account_dropdown() -> dcc.Dropdown:
    with MainSessionLocal() as session:
        accounts = session.query(Account).filter_by(platform=Platform.METATRADER.value, enabled=True).all()

    return dcc.Dropdown(
        id="account-dropdown",
        options=[{"label": "All Accounts", "value": "ALL"}] + [{"label": a.uid, "value": a.uid} for a in accounts],
        value="ALL",
        clearable=False,
        style={"width": "300px", "marginBottom": "20px"},
    )


def _render_chart(  # pylint: disable=too-many-arguments, too-many-positional-arguments
    metric, df: pd.DataFrame, y_col: str, title: str, y_axis_title: str, y_range=None, split_by_account=True
) -> AlphaCol:
    result = metric.calculate(df)
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
                    y_range=y_range,
                ),
            ).plot(x_col="time", y_col=y_col, group_by="account_id" if split_by_account else None)
        ),
        xs=12,
        sm=12,
        md=12,
        lg=6,
        xl=6,
    )


class PerformancePage(BasePage):
    """Performance Page."""

    def render(self):
        return PageBody(
            [
                PageHeader(self._title).render(),
                MainContent(
                    [
                        AlphaTabToolbar(
                            tab_labels=TAB_LABELS,
                            base_href="/analytics",
                            current_tab="performance",
                            link_with_hash=False,
                        ).render(),
                        _render_account_dropdown(),
                        dcc.Loading(html.Div(id="performance-content")),
                    ]
                ),
            ]
        )


layout = PerformancePage("Performance").layout


@callback(
    Output("performance-content", "children"),
    Input("account-dropdown", "value"),
)
def render_performance_tab(selected_account):
    """Render the performance tab."""
    trades = get_all_trades()
    if not trades:
        return dbc.Alert("⚠️ No trade data found.", color="warning")

    data_frame = pd.DataFrame([t.__dict__ for t in trades])
    data_frame = data_frame[[col for col in data_frame.columns if not col.startswith("_sa_")]]

    if selected_account != "ALL":
        data_frame = data_frame[data_frame["account_id"] == selected_account]

    if data_frame.empty:
        return dbc.Alert("⚠️ No trade data available for the selected account.", color="warning")

    expectancy_df = ExpectancyOverTime().calculate(data_frame)
    # rel_df = ExpectancyOverTimeRelative().calculate(data_frame)
    # pf_df = ProfitFactorOverTime().calculate(data_frame)
    # rr_df = RiskRewardRatioOverTime().calculate(data_frame)
    # sharpe_df = SharpeRatioOverTime().calculate(data_frame)
    # sortino_df = SortinoRatioOverTime().calculate(data_frame)

    return AlphaRow(
        [
            AlphaCol(
                ExpectancyOverTimeMolecule(expectancy_df).render(),
                xs=12,
                sm=12,
                md=12,
                lg=6,
                xl=6,
            ),
            # AlphaCol(
            #     ProfitFactorOverTimeMolecule(pf_df).render(),
            #     xs=12,
            #     sm=12,
            #     md=12,
            #     lg=6,
            #     xl=4,
            # ),
            # AlphaCol(
            #     RiskRewardOverTimeMolecule(rr_df).render(),
            #     xs=12,
            #     sm=12,
            #     md=12,
            #     lg=6,
            #     xl=4,
            # ),
            # AlphaCol(
            #     SharpeRatioOverTimeMolecule(sharpe_df).render(),
            #     xs=12,
            #     sm=12,
            #     md=12,
            #     lg=6,
            #     xl=4,
            # ),
            # AlphaCol(
            #     SortinoRatioOverTimeMolecule(sortino_df).render(),
            #     xs=12,
            #     sm=12,
            #     md=12,
            #     lg=6,
            #     xl=4,
            # ),
        ]
    )
