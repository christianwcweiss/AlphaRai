import dash
import dash_bootstrap_components as dbc
import pandas as pd
from dash import html, dcc, Input, Output, callback

from components.atoms.content import MainContent
from components.atoms.layout.layout import AlphaRow, AlphaCol
from components.atoms.tabbar.tabbar import AlphaTabToolbar
from components.atoms.text.page import PageHeader
from components.frame.body import PageBody
from components.molecules.charts.trades_per_day_over_time.trades_per_day_over_time import TradesPerDayOverTimeMolecule
from components.molecules.charts.win_rate_over_time.win_rate_over_time import WinRateOverTimeMolecule
from db.database import MainSessionLocal
from models.main.account import Account
from pages.analytics.analysis import TAB_LABELS
from pages.base_page import BasePage
from quant_core.enums.platform import Platform
from quant_core.metrics.trades_per_day_over_time.trades_per_day import TradesPerDayOverTime
from quant_core.metrics.win_rate_over_time.win_rate_over_time import WinRateOverTime
from services.db.cache.trade_history import get_all_trades

dash.register_page(__name__, path="/analytics/behavior", name="Behavior")


def _render_account_dropdown() -> dcc.Dropdown:
    with MainSessionLocal() as session:
        accounts = session.query(Account).filter_by(platform=Platform.METATRADER.value, enabled=True).all()

    return dcc.Dropdown(
        id="behavior-account-dropdown",
        options=[{"label": "All Accounts", "value": "ALL"}] + [{"label": a.uid, "value": a.uid} for a in accounts],
        value="ALL",
        clearable=False,
        style={"width": "300px", "marginBottom": "20px"},
    )


class BehaviorPage(BasePage):
    """Behavior Page."""

    def render(self):
        return PageBody(
            [
                PageHeader(self._title).render(),
                MainContent(
                    [
                        AlphaTabToolbar(
                            tab_labels=TAB_LABELS,
                            base_href="/analytics",
                            current_tab="behavior",
                            link_with_hash=False,
                        ).render(),
                        _render_account_dropdown(),
                        dcc.Loading(html.Div(id="behavior-content")),
                    ]
                ),
            ]
        )


layout = BehaviorPage("Behavior").layout


@callback(
    Output("behavior-content", "children"),
    Input("behavior-account-dropdown", "value"),
)
def render_behaviour_tab(selected_account):
    """Render the behavior tab."""
    trades = get_all_trades()
    if not trades:
        return dbc.Alert("⚠️ No trade data found.", color="warning")

    df = pd.DataFrame([t.__dict__ for t in trades])
    df = df[[col for col in df.columns if not col.startswith("_sa_")]]

    if selected_account != "ALL":
        df = df[df["account_id"] == selected_account]

    if df.empty:
        return dbc.Alert("⚠️ No trade data available for the selected account.", color="warning")

    win_rate_metric_df = WinRateOverTime().calculate(df)
    trades_per_day_metric_df = TradesPerDayOverTime().calculate(df)

    return AlphaRow(
        [
            AlphaCol(
                WinRateOverTimeMolecule(win_rate_metric_df).render(),
                xs=12,
                sm=12,
                md=12,
                lg=6,
                xl=4,
            ),
            AlphaCol(
                TradesPerDayOverTimeMolecule(trades_per_day_metric_df).render(),
                xs=12,
                sm=12,
                md=12,
                lg=6,
                xl=4,
            ),
        ]
    )
