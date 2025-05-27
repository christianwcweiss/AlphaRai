from typing import Tuple

import dash
import dash_bootstrap_components as dbc
from dash import html, dcc, Input, Output, State, callback

from components.atoms.content import MainContent
from components.atoms.text.page import PageHeader
from components.frame.body import PageBody
from pages.base_page import BasePage
from quant_core.enums.asset_type import AssetType
from quant_core.enums.stagger_method import StaggerMethod
from services.db.main.account import get_account_by_uid
from services.db.main.account_config import get_configs_by_account_id, upsert_config

dash.register_page(__name__, path_template="/settings/symbol/<uid>/<asset_id>", name="Symbol Settings Detail")


class SymbolSettingsPage(BasePage):
    """Symbol Settings Page."""

    def render(self):
        return PageBody(
            [
                dcc.Location(id="symbol-url"),
                html.Div(id="symbol-uid", style={"display": "none"}),
                html.Div(id="symbol-asset-id", style={"display": "none"}),
                html.Div(id="dynamic-header"),
                MainContent(
                    [
                        dbc.Form(
                            [
                                dbc.Label("Signal Asset ID"),
                                dbc.Input(id="input-signal-id"),
                                dbc.Label("Platform Asset ID"),
                                dbc.Input(id="input-platform-id"),
                                dbc.Label("Entry Stagger Method"),
                                dbc.Select(
                                    id="input-entry-stagger",
                                    options=[{"label": m.value.capitalize(), "value": m.value} for m in StaggerMethod],
                                ),
                                dbc.Label("# Staggers"),
                                dbc.Input(id="input-n-staggers", type="number", min=1),
                                dbc.Label("Risk %"),
                                dbc.Input(id="input-risk", type="number", step=0.01, min=0),
                                dbc.Label("Lot Size"),
                                dbc.Input(id="input-lot-size", type="number", step=0.01, min=0),
                                dbc.Label("Decimals"),
                                dbc.Input(id="input-decimals", type="number", step=1, min=0),
                                dbc.Label("Asset Type"),
                                dbc.Select(
                                    id="input-asset-type",
                                    options=[{"label": a.value.capitalize(), "value": a.value} for a in AssetType],
                                ),
                                dbc.Switch(id="input-enabled", label="Enabled"),
                                html.Br(),
                                dbc.Button("Save", id="save-symbol-settings", color="primary"),
                            ]
                        )
                    ]
                ),
            ]
        )


layout = SymbolSettingsPage("Symbol Settings").layout


@callback(
    Output("symbol-uid", "children"),
    Output("symbol-asset-id", "children"),
    Output("dynamic-header", "children", allow_duplicate=True),
    Output("input-signal-id", "value"),
    Output("input-platform-id", "value"),
    Output("input-entry-stagger", "value"),
    Output("input-n-staggers", "value"),
    Output("input-risk", "value"),
    Output("input-lot-size", "value"),
    Output("input-decimals", "value"),
    Output("input-asset-type", "value"),
    Output("input-enabled", "value"),
    Input("symbol-url", "pathname"),
    prevent_initial_call=True,
)
def load_config(pathname: str) -> Tuple[
    str,
    str,
    html.Div,
    str,
    str,
    str,
    int,
    float,
    float,
    int,
    AssetType,
    bool,
]:
    """Load the configuration for the symbol settings page."""
    try:
        parts = pathname.strip("/").split("/")
        uid = parts[2]
        asset_id = parts[3]
    except (IndexError, ValueError):
        raise dash.exceptions.PreventUpdate  # pylint: disable=raise-missing-from

    account = get_account_by_uid(uid)
    if not account:
        raise dash.exceptions.PreventUpdate

    config = next((c for c in get_configs_by_account_id(uid) if c.signal_asset_id == asset_id), None)
    if not config:
        raise dash.exceptions.PreventUpdate

    return (
        uid,
        asset_id,
        PageHeader(f'Settings for "{asset_id}"').render(),
        config.signal_asset_id,
        config.platform_asset_id,
        config.entry_stagger_method,
        config.n_staggers,
        config.risk_percent,
        config.lot_size,
        config.decimal_points,
        config.asset_type,
        config.enabled,
    )


@callback(
    Output("input-platform-id", "value", allow_duplicate=True),
    Input("save-symbol-settings", "n_clicks"),
    State("symbol-uid", "children"),
    State("input-signal-id", "value"),
    State("input-platform-id", "value"),
    State("input-entry-stagger", "value"),
    State("input-n-staggers", "value"),
    State("input-risk", "value"),
    State("input-lot-size", "value"),
    State("input-decimals", "value"),
    State("input-asset-type", "value"),
    State("input-enabled", "value"),
    prevent_initial_call=True,
)
def save_symbol_settings(  # pylint: disable=too-many-arguments, too-many-positional-arguments
    _,
    uid: str,
    signal_id: str,
    platform_id: str,
    entry_stagger: str,
    n_staggers: int,
    risk: float,
    lot_size: float,
    decimals: int,
    asset_type: str,
    enabled: bool,
) -> str:
    """Save the symbol settings."""
    if not uid or not signal_id:
        raise dash.exceptions.PreventUpdate

    upsert_config(
        uid,
        {
            "signal_asset_id": signal_id,
            "platform_asset_id": platform_id,
            "entry_stagger_method": entry_stagger,
            "n_staggers": n_staggers,
            "risk_percent": risk,
            "lot_size": lot_size,
            "decimal_points": decimals,
            "asset_type": asset_type,
            "enabled": enabled,
        },
    )

    return platform_id
