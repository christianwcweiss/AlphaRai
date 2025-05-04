import dash
import dash_bootstrap_components as dbc
import pandas as pd
from dash import html, dcc, callback, Input, Output, State

from components.atoms.content import MainContent
from components.atoms.layout.layout import AlphaCol, AlphaRow
from components.atoms.tabbar.tabbar import AlphaTabToolbar
from components.atoms.text.page import PageHeader
from components.frame.body import PageBody
from db.database import SessionLocal
from models.account import Account
from pages.base_page import BasePage
from quant_core.enums.platform import Platform
from quant_core.services.core_logger import CoreLogger
from services.db.trade_history import get_all_trades

# Tab content render functions
from pages.analytics.tabs.overview import render as render_overview
from pages.analytics.tabs.performance import render as render_performance
from pages.analytics.tabs.behaviour_and_time import render as render_behavior
from pages.analytics.tabs.symbol_breakdown import render as render_breakdown
from pages.analytics.tabs.costs import render as render_costs
from pages.analytics.tabs.trade_list import render as render_trade_list

dash.register_page(__name__, path="/analysis", name="Analysis")


def _render_account_dropdown() -> html.Div:
    with SessionLocal() as session:
        accounts = session.query(Account).filter_by(platform=Platform.METATRADER.value, enabled=True).all()

    options = [{"label": "All Accounts", "value": "ALL"}] + [
        {"label": account.uid, "value": account.uid} for account in accounts
    ]

    return html.Div(
        dcc.Dropdown(
            id="account-dropdown",
            options=options,
            value="ALL",
            clearable=False,
            style={"width": "300px", "marginBottom": "20px"},
        )
    )


class AnalysisPage(BasePage):
    def render(self):
        return PageBody(
            [
                PageHeader("Analysis").render(),
                MainContent(
                    [
                        dcc.Location(id="url", refresh=False),
                        _render_account_dropdown(),
                        dcc.Loading(html.Div(id="analysis-output"), type="circle"),
                    ]
                ),
            ]
        )


page = AnalysisPage("Strategy Analysis")
layout = page.layout


@callback(
    Output("analysis-output", "children"),
    Input("url", "hash"),
    Input("account-dropdown", "value"),
)
def render_tab_from_hash(url_hash, selected_account):
    tab = url_hash.lstrip("#$") if url_hash else "overview"
    CoreLogger().info(f"📊 Tab via hash: {tab} | Account: {selected_account}")

    trades = get_all_trades()
    if not trades:
        return dbc.Alert("⚠️ No trade data found.", color="warning")

    df = pd.DataFrame([t.__dict__ for t in trades])
    df = df[[col for col in df.columns if not col.startswith("_sa_")]]  # Remove SQLAlchemy internal columns

    if selected_account != "ALL":
        df = df[df["account_id"] == selected_account]

    if df.empty:
        return dbc.Alert("⚠️ No trade data available for the selected account.", color="warning")

    render_map = {
        "overview": render_overview,
        "performance": render_performance,
        "behavior": render_behavior,
        "breakdown": render_breakdown,
        "costs": render_costs,
        "trade_list": render_trade_list,
    }

    render_fn = render_map.get(tab, render_overview)
    tab_ids = list(render_map.keys())

    tabbar = AlphaTabToolbar(
        tab_labels=tab_ids,
        base_href="/analysis",
        current_tab=tab,
    ).render()

    return html.Div([
        tabbar,
        html.Div(render_fn(df))
    ])
