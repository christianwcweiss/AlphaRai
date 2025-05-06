import dash
import pandas as pd
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
from dash import html, dcc, Input, Output, State, callback

from components.atoms.tabbar.tabbar import AlphaTabToolbar
from components.atoms.text.page import PageHeader
from components.atoms.content import MainContent
from components.frame.body import PageBody
from components.atoms.layout.layout import AlphaRow, AlphaCol
from components.molecules.charts.balance_over_time.balance_over_time import BalanceOverTime
from db.database import SessionLocal
from models.account import Account
from pages.analytics.analysis import TAB_LABELS
from pages.base_page import BasePage
from quant_core.enums.platform import Platform
from services.db.trade_history import get_all_trades
from quant_core.metrics.account_balance_over_time.absolute.balance_over_time import AccountBalanceOverTimeAbsolute
from quant_core.metrics.account_balance_over_time.relative.balance_over_time import AccountBalanceOverTimeRelative

dash.register_page(__name__, path="/analysis/overview", name="Overview")


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


class AnalysisOverviewPage(BasePage):
    def render(self):
        return PageBody([
            PageHeader(self._title).render(),
            MainContent([
                AlphaTabToolbar(
                    tab_labels=TAB_LABELS,
                    base_href="/analysis",
                    current_tab="overview",
                    link_with_hash=False
                ).render(),                _render_account_dropdown(),
                dcc.Loading(html.Div(id="overview-content")),
            ]),
        ])


layout = AnalysisOverviewPage("Overview").layout


@callback(
    Output("overview-content", "children"),
    Input("account-dropdown", "value"),
)
def render_overview_tab(selected_account):
    trades = get_all_trades()
    if not trades:
        return dbc.Alert("⚠️ No trade data found.", color="warning")

    df = pd.DataFrame([t.__dict__ for t in trades])
    df = df[[col for col in df.columns if not col.startswith("_sa_")]]

    if selected_account != "ALL":
        df = df[df["account_id"] == selected_account]

    if df.empty:
        return dbc.Alert("⚠️ No trade data available for the selected account.", color="warning")

    absolute_metric = AccountBalanceOverTimeAbsolute()
    relative_metric = AccountBalanceOverTimeRelative()

    abs_df = absolute_metric.calculate_grouped(df)
    rel_df = relative_metric.calculate_grouped(df)

    return AlphaRow([
        AlphaCol(
            BalanceOverTime(abs_df, rel_df).render(),
            xs=12,
            sm=12,
            md=12,
            lg=6,
            xl=6,
        )
    ])
