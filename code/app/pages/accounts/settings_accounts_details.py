import dash
import dash_bootstrap_components as dbc
from dash import html, dcc, Input, Output, State, callback

from components.atoms.content import MainContent
from components.atoms.layout.layout import AlphaRow, AlphaCol
from components.atoms.table.table import AlphaTable
from components.atoms.text.page import PageHeader
from components.frame.body import PageBody
from pages.base_page import BasePage
from services.db.account import get_account_by_uid
from services.db.account_config import get_configs_by_account_id, sync_with_mt5

dash.register_page(__name__, path_template="/settings/accounts/<uid>", name="Account Settings Details")


# Build the configurations table for enabled or disabled configs
def build_table(account_id: str, enabled: bool) -> html.Div:
    configs = get_configs_by_account_id(account_id)
    filtered = [c for c in configs if c.enabled == enabled]

    if not filtered:
        return html.Div("No symbols found." if enabled else "No disabled symbols.")

    headers = [
        "Signal Asset ID",
        "Platform Asset ID",
        "Entry Stagger",
        "# Staggers",
        "Risk %",
        "Lot Size",
        "Decimals",
        "Details",
    ]

    rows = [
        [
            c.signal_asset_id,
            c.platform_asset_id,
            c.entry_stagger_method,
            str(c.n_staggers),
            str(c.risk_percent),
            str(c.lot_size),
            str(c.decimal_points),
            dcc.Link("🔍 View", href=f"/settings/symbol/{account_id}/{c.signal_asset_id}"),
        ]
        for c in sorted(filtered, key=lambda x: x.signal_asset_id)
    ]

    title = html.H5("✅ Enabled Symbols") if enabled else html.H5("❌ Disabled Symbols")
    return html.Div([title, AlphaTable(table_id=f"table-{enabled}", headers=headers, rows=rows).render()])


# Settings Details Page class
class SettingsDetailsPage(BasePage):
    def render(self):
        return PageBody(
            [
                dcc.Location(id="settings-url"),
                html.Div(id="settings-uid", style={"display": "none"}),
                html.Div(id="dynamic-header"),
                MainContent(
                    [
                        html.Div(id="table-container"),
                        html.Br(),
                        AlphaRow(
                            [
                                AlphaCol(
                                    dbc.Button("🔄 Sync with MT5", id="sync-mt5-btn", color="primary"),
                                    width="auto",
                                ),
                            ]
                        ),
                    ]
                ),
            ]
        )


layout = SettingsDetailsPage("Settings Details").layout


# Extract UID from URL and display dynamic header
@callback(
    Output("settings-uid", "children"),
    Output("dynamic-header", "children"),
    Input("settings-url", "pathname"),
    prevent_initial_call=True,
)
def extract_uid_from_url(pathname: str):
    uid = pathname.split("/")[-1]
    account = get_account_by_uid(uid)
    if not account:
        raise dash.exceptions.PreventUpdate
    return uid, PageHeader(f'Trade Settings for "{account.friendly_name}"').render()


# Render both enabled and disabled configuration tables
@callback(
    Output("table-container", "children"),
    Input("settings-uid", "children"),
    prevent_initial_call=True,
)
def render_table(uid):
    return html.Div([
        build_table(uid, enabled=True),
        html.Hr(),
        build_table(uid, enabled=False),
    ])


# Sync with MT5 callback
@callback(
    Output("table-container", "children", allow_duplicate=True),
    Input("sync-mt5-btn", "n_clicks"),
    State("settings-uid", "children"),
    prevent_initial_call=True,
)
def sync_symbols_callback(_, uid):
    account = get_account_by_uid(uid)
    if not account:
        raise dash.exceptions.PreventUpdate

    sync_with_mt5(account_id=uid, secret_id=account.secret_name)
    return render_table(uid)
