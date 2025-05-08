import dash
import dash_bootstrap_components as dbc
from dash import html, dcc, Input, Output, State, ctx, callback, ALL

from components.atoms.buttons.button import AlphaButton
from components.atoms.content import MainContent
from components.atoms.layout.layout import AlphaRow, AlphaCol
from components.atoms.modal.modal import AlphaModal
from components.atoms.table.table import AlphaTable
from components.atoms.text.page import PageHeader
from components.frame.body import PageBody
from pages.base_page import BasePage
from quant_core.enums.asset_type import AssetType
from quant_core.enums.stagger_method import StaggerMethod
from services.db.account import get_account_by_uid
from services.db.account_config import (
    get_configs_by_account_id,
    upsert_config,
    delete_config,
    delete_all_configs,
    sync_with_mt5,
)

dash.register_page(__name__, path_template="/settings/accounts/<uid>", name="Account Settings Details")


# Configuration modal fields
def _config_modal_fields(
    prefix: str,
    signal_asset_id="",
    platform_asset_id="",
    entry_stagger="",
    n_staggers=1,
    risk_percent=1.0,
    lot_size=0.01,
    decimals=2,
    asset_type: str = "",
):
    return html.Div(
        [
            dbc.Input(
                id=f"{prefix}-signal-asset-id", value=signal_asset_id, placeholder="Signal Asset ID", className="mb-2"
            ),
            dbc.Input(
                id=f"{prefix}-platform-asset-id",
                value=platform_asset_id,
                placeholder="Platform Asset ID",
                className="mb-2",
            ),
            dbc.Select(
                id=f"{prefix}-entry-stagger",
                options=[{"label": m.value.capitalize(), "value": m.value} for m in StaggerMethod],
                value=entry_stagger or StaggerMethod.LINEAR.value,
                className="mb-2",
            ),
            dbc.Input(
                id=f"{prefix}-n-staggers",
                type="number",
                value=n_staggers,
                min=1,
                className="mb-2",
                placeholder="Staggers",
            ),
            dbc.Input(
                id=f"{prefix}-risk",
                type="number",
                value=risk_percent,
                step=0.01,
                min=0.0,
                className="mb-2",
                placeholder="Risk %",
            ),
            dbc.Input(
                id=f"{prefix}-lot-size",
                type="number",
                value=lot_size,
                step=0.01,
                min=0.0,
                className="mb-2",
                placeholder="Lot Size",
            ),
            dbc.Input(
                id=f"{prefix}-decimals",
                type="number",
                value=decimals,
                step=1,
                min=0,
                className="mb-2",
                placeholder="Decimals",
            ),
            dbc.Select(
                id=f"{prefix}-asset-type",
                options=[{"label": a.value.capitalize(), "value": a.value} for a in AssetType],
                value=asset_type or None,
                placeholder="Asset Type",
                className="mb-2",
            ),
        ]
    )


# Action buttons for each configuration
def _action_buttons(signal_asset_id: str):
    return AlphaRow(
        [
            AlphaCol(
                AlphaButton(
                    "✏️",
                    {"type": "edit-config", "index": signal_asset_id},
                    style={"backgroundColor": "#FFC107", "width": "40px"},
                ).render(),
                width="auto",
            ),
            AlphaCol(
                AlphaButton(
                    "🗑️",
                    {"type": "delete-config", "index": signal_asset_id},
                    style={"backgroundColor": "#DC3545", "width": "40px"},
                ).render(),
                width="auto",
            ),
        ]
    )


# Enabled toggle button
def _enabled_button(account_id: str, signal_asset_id: str, is_enabled: bool):
    label = "✅" if is_enabled else "❌"
    color = "#198754" if is_enabled else "#6c757d"
    return AlphaButton(
        label,
        {
            "type": "toggle-enabled",
            "account": account_id,
            "index": signal_asset_id,
        },
        style={"backgroundColor": color, "width": "40px"},
    ).render()


# Build the configurations table
def build_table(account_id: str) -> html.Table:
    configs = get_configs_by_account_id(account_id)
    headers = [
        "Signal Asset ID",
        "Platform Asset ID",
        "Entry Stagger",
        "# Staggers",
        "Risk %",
        "Lot Size",
        "Decimals",
        "Enabled",
        "Actions",
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
            _enabled_button(account_id, c.signal_asset_id, c.enabled),
            _action_buttons(c.signal_asset_id),
        ]
        for c in sorted(configs, key=lambda x: x.signal_asset_id)
    ]

    return AlphaTable(table_id="details-table", headers=headers, rows=rows).render()


# Settings Details Page
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
                                AlphaCol(AlphaButton("➕ Add Config", "open-add-config-btn").render(), width="auto"),
                                AlphaCol(AlphaButton("🔄 Sync with MT5", "sync-mt5-btn").render(), width="auto"),
                                AlphaCol(
                                    AlphaButton(
                                        "🧨 Delete All Configs",
                                        "delete-all-configs-btn",
                                        style={"backgroundColor": "#dc3545"},
                                    ).render(),
                                    width="auto",
                                ),
                            ]
                        ),
                        AlphaModal(
                            "add-config-modal",
                            "Add New Config",
                            _config_modal_fields("modal-add"),
                            "confirm-add-config",
                            "cancel-add-config",
                        ).render(),
                        AlphaModal(
                            "edit-config-modal",
                            "Edit Config",
                            _config_modal_fields("modal-edit"),
                            "confirm-edit-config",
                            "cancel-edit-config",
                        ).render(),
                    ]
                ),
            ]
        )


layout = SettingsDetailsPage("Settings Details").layout


# Extract UID from URL
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


# Render the configurations table
@callback(Output("table-container", "children"), Input("settings-uid", "children"), prevent_initial_call=True)
def render_table(uid):
    return build_table(uid)


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
    return build_table(uid)


# Delete all configurations callback
@callback(
    Output("table-container", "children", allow_duplicate=True),
    Input("delete-all-configs-btn", "n_clicks"),
    State("settings-uid", "children"),
    prevent_initial_call=True,
)
def delete_all_configs_callback(_, uid):
    delete_all_configs(uid)
    return build_table(uid)


# Toggle add config modal
@callback(
    Output("add-config-modal", "is_open"),
    Output("modal-tracker-store", "data"),
    Input("open-add-config-btn", "n_clicks"),
    Input("confirm-add-config", "n_clicks"),
    Input("cancel-add-config", "n_clicks"),
    State("modal-tracker-store", "data"),
    prevent_initial_call=True,
)
def toggle_add_modal(open_clicks, confirm_clicks, cancel_clicks, tracker_data):
    triggered = ctx.triggered_id
    open_count = tracker_data.get("open_clicks", 0)

    if triggered == "open-add-config-btn" and open_clicks > open_count:
        return True, {"open_clicks": open_clicks}

    return False, tracker_data


# Open edit config modal
@callback(
    Output("edit-config-modal", "is_open"),
    Output("modal-edit-signal-asset-id", "value"),
    Output("modal-edit-platform-asset-id", "value"),
    Output("modal-edit-entry-stagger", "value"),
    Output("modal-edit-n-staggers", "value"),
    Output("modal-edit-risk", "value"),
    Output("modal-edit-lot-size", "value"),
    Output("modal-edit-decimals", "value"),
    Input({"type": "edit-config", "index": ALL}, "n_clicks"),
    State("settings-uid", "children"),
    prevent_initial_call=True,
)
def open_edit_modal(n_clicks_list, account_id):
    triggered = ctx.triggered_id
    if not isinstance(triggered, dict) or triggered.get("type") != "edit-config":
        raise dash.exceptions.PreventUpdate

    if not any(n_clicks_list):
        raise dash.exceptions.PreventUpdate

    config = next((c for c in get_configs_by_account_id(account_id) if c.signal_asset_id == triggered["index"]), None)
    if not config:
        raise dash.exceptions.PreventUpdate

    return (
        True,
        config.signal_asset_id,
        config.platform_asset_id,
        config.entry_stagger_method,
        config.n_staggers,
        config.risk_percent,
        config.lot_size,
        config.decimal_points,
    )


# Save new configuration
@callback(
    Output("table-container", "children", allow_duplicate=True),
    Input("confirm-add-config", "n_clicks"),
    State("settings-uid", "children"),
    State("modal-add-signal-asset-id", "value"),
    State("modal-add-platform-asset-id", "value"),
    State("modal-add-entry-stagger", "value"),
    State("modal-add-n-staggers", "value"),
    State("modal-add-risk", "value"),
    State("modal-add-lot-size", "value"),
    State("modal-add-decimals", "value"),
    State("modal-add-asset-type", "value"),
    prevent_initial_call=True,
)
def save_new_config(_, uid, signal_id, platform_id, entry_stagger, n_staggers, risk, lot_size, decimals, asset_type):
    if not signal_id or not platform_id:
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
        },
    )

    return build_table(uid)


@callback(
    Output("table-container", "children", allow_duplicate=True),
    Input("confirm-edit-config", "n_clicks"),
    State("settings-uid", "children"),
    State("modal-edit-signal-asset-id", "value"),
    State("modal-edit-platform-asset-id", "value"),
    State("modal-edit-entry-stagger", "value"),
    State("modal-edit-n-staggers", "value"),
    State("modal-edit-risk", "value"),
    State("modal-edit-lot-size", "value"),  # ✅ Add this line
    State("modal-edit-decimals", "value"),
    prevent_initial_call=True,
)
def save_edited_config(_, uid, signal_id, platform_id, entry_stagger, n_staggers, risk, lot_size, decimals):
    if not signal_id or not platform_id:
        raise dash.exceptions.PreventUpdate

    upsert_config(
        uid,
        {
            "signal_asset_id": signal_id,
            "platform_asset_id": platform_id,
            "entry_stagger_method": entry_stagger,
            "n_staggers": n_staggers,
            "risk_percent": risk,
            "lot_size": lot_size,  # ✅ Include this in the update
            "decimal_points": decimals,
        },
    )

    return build_table(uid)


# Handle delete configuration
@callback(
    Output("table-container", "children", allow_duplicate=True),
    Input({"type": "delete-config", "index": ALL}, "n_clicks"),
    State("settings-uid", "children"),
    prevent_initial_call=True,
)
def handle_delete_config(delete_clicks, uid):
    triggered = ctx.triggered_id
    if not isinstance(triggered, dict):
        raise dash.exceptions.PreventUpdate
    if not any(delete_clicks):
        raise dash.exceptions.PreventUpdate
    delete_config(uid, triggered["index"])
    return build_table(uid)


@callback(
    Output("table-container", "children", allow_duplicate=True),
    Input({"type": "toggle-enabled", "account": ALL, "index": ALL}, "n_clicks"),
    State("settings-uid", "children"),
    prevent_initial_call=True,
)
def toggle_enabled_callback(n_clicks_list, uid):
    # Catch valid trigger only
    triggered = ctx.triggered_id
    if not isinstance(triggered, dict) or triggered.get("type") != "toggle-enabled":
        raise dash.exceptions.PreventUpdate

    # Check which button was actually clicked
    input_ids = ctx.inputs_list[0]  # list of {"id": ..., "property": "n_clicks"}
    try:
        triggered_index = next(i for i, entry in enumerate(input_ids) if entry["id"] == triggered)
    except StopIteration:
        raise dash.exceptions.PreventUpdate

    if n_clicks_list[triggered_index] in (None, 0):
        # Not actually clicked (page reload or table rebuild)
        raise dash.exceptions.PreventUpdate

    signal_id = triggered["index"]

    config = next((c for c in get_configs_by_account_id(uid) if c.signal_asset_id == signal_id), None)
    if not config:
        raise dash.exceptions.PreventUpdate

    upsert_config(
        uid,
        {
            "signal_asset_id": config.signal_asset_id,
            "platform_asset_id": config.platform_asset_id,
            "entry_stagger_method": config.entry_stagger_method,
            "n_staggers": config.n_staggers,
            "risk_percent": config.risk_percent,
            "lot_size": config.lot_size,
            "decimal_points": config.decimal_points,
            "enabled": not config.enabled,
            "asset_type": config.asset_type,
        },
    )

    return build_table(uid)
