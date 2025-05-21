import dash
import dash_bootstrap_components as dbc
from dash import Input, Output, dcc, html, callback

from components.atoms.content import MainContent
from components.atoms.layout.layout import AlphaRow, AlphaCol
from components.atoms.tabbar.tabbar import AlphaTabToolbar
from components.atoms.text.page import PageHeader
from components.frame.body import PageBody
from components.molecules.charts.balance_over_time.balance_over_time import BalanceOverTime
from components.molecules.toolbars.analytics_toolbar import AnalyticsToolbarMolecule
from pages.analytics.analysis import TAB_LABELS
from pages.base_page import BasePage
from quant_core.metrics.account_balance_over_time.balance_over_time import AccountBalanceOverTime
from services.db.cache.trade_history import get_all_trades_df

dash.register_page(__name__, path="/analytics/overview", name="Overview")


class AnalysisOverviewPage(BasePage):
    """Overview Page for Analytics."""

    def render(self):
        return PageBody(
            [
                PageHeader(self._title).render(),
                MainContent(
                    [
                        AlphaTabToolbar(
                            tab_labels=TAB_LABELS,
                            base_href="/analytics",
                            current_tab="overview",
                            link_with_hash=False,
                        ).render(),
                        AnalyticsToolbarMolecule().render(),  # Replaces _render_account_dropdown()
                        dcc.Loading(html.Div(id="overview-content")),
                    ]
                ),
            ]
        )


layout = AnalysisOverviewPage("Overview").layout


@callback(
    Output("filter-by-account_id", "options"),
    Output("filter-by-symbol", "options"),
    Output("filter-by-asset-type", "options"),
    Input("account-dropdown", "value"),
)
def load_filter_options(_):  # placeholder, can change trigger if needed
    trades_df = get_all_trades_df()
    if trades_df.empty:
        return [], [], []

    return [
        [{"label": val, "value": val} for val in sorted(trades_df["account_id"].unique())],
        [{"label": val, "value": val} for val in sorted(trades_df["symbol"].unique())],
        [{"label": val, "value": val} for val in sorted(trades_df["asset_type"].unique())],
    ]


@callback(
    Output("overview-content", "children"),
    Input("filter-by-account_id", "value"),
    Input("filter-by-symbol", "value"),
    Input("filter-by-asset-type", "value"),
    Input("group-by-account_id", "n_clicks"),
    Input("group-by-symbol", "n_clicks"),
    Input("group-by-asset-type", "n_clicks"),
    Input("group-by-hour", "n_clicks"),
    Input("group-by-weekday", "n_clicks"),
)
def render_overview_tab(account_ids, symbols, asset_types, *group_clicks):
    trades_df = get_all_trades_df()

    if account_ids:
        trades_df = trades_df[trades_df["account_id"].isin(account_ids)]
    if symbols:
        trades_df = trades_df[trades_df["symbol"].isin(symbols)]
    if asset_types:
        trades_df = trades_df[trades_df["asset_type"].isin(asset_types)]

    if trades_df.empty:
        return dbc.Alert("⚠️ No trade data found.", color="warning")

    group_ids = ["account_id", "symbol", "asset_type", "hour", "weekday"]
    active_groups = [group_ids[i] for i, clicks in enumerate(group_clicks) if clicks and clicks % 2 == 1]

    kwargs = {f"group_by_{g}": True for g in ["account_id", "symbol", "asset_type", "hour", "weekday"]}
    for g in kwargs:
        if g.replace("group_by_", "") not in active_groups:
            kwargs[g] = False

    balance_over_time_data_frame = AccountBalanceOverTime().calculate(trades_df, **kwargs)

    return AlphaRow(
        [
            AlphaCol(
                BalanceOverTime(balance_over_time_data_frame).render(),
                xs=12,
                sm=12,
                md=12,
                lg=6,
                xl=6,
            )
        ]
    )


GROUP_BY_IDS = [
    "group-by-account_id",
    "group-by-symbol",
    "group-by-asset-type",
    "group-by-hour",
    "group-by-weekday",
]


@callback(
    [Output(button_id, "active") for button_id in GROUP_BY_IDS],
    [Input(button_id, "n_clicks") for button_id in GROUP_BY_IDS],
    prevent_initial_call=True,
)
def update_group_by_buttons(*clicks):
    return [click % 2 == 1 for click in clicks]
