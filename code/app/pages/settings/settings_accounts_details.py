import dash
import dash_bootstrap_components as dbc
from dash import html, Input, Output, State, ctx, dcc, callback, ALL

from components.atoms.buttons.button import AlphaButton
from components.atoms.content import MainContent
from components.atoms.layout.layout import AlphaRow, AlphaCol
from components.atoms.modal.modal import AlphaModal
from components.atoms.table.table import AlphaTable
from components.atoms.text.page import PageHeader
from components.frame.body import PageBody
from pages.base_page import BasePage
from quant_core.enums.stagger_method import StaggerMethod
from quant_core.services.core_logger import CoreLogger
from services.db.accounts import get_account_by_uid
from services.db.trade_config import get_configs_by_uid, upsert_config, delete_config

dash.register_page(__name__, path_template="/settings/accounts/<uid>", name="Account Settings Details")

# --- Helper Functions ---


def _config_modal_fields(
    prefix: str,
    signal_asset_id="",
    platform_asset_id="",
    entry_stagger="",
    size_stagger="",
    n_staggers=1,
    size=0.0,
    decimals=2,
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
            dbc.Select(
                id=f"{prefix}-size-stagger",
                options=[{"label": m.value.capitalize(), "value": m.value} for m in StaggerMethod],
                value=size_stagger or StaggerMethod.LINEAR.value,
                className="mb-2",
            ),
            dbc.Input(
                id=f"{prefix}-n-staggers",
                type="number",
                min=1,
                value=n_staggers,
                placeholder="# Staggers",
                className="mb-2",
            ),
            dbc.Input(id=f"{prefix}-size", type="number", step=0.01, value=size, placeholder="Size", className="mb-2"),
            dbc.Input(
                id=f"{prefix}-decimals",
                type="number",
                min=0,
                step=1,
                value=decimals,
                placeholder="Decimals",
                className="mb-2",
            ),
        ]
    )


def _action_buttons(signal_asset_id: str) -> html.Div:
    return AlphaRow(
        [
            AlphaCol(
                AlphaButton(
                    "✏️",
                    button_id={"type": "edit-config", "index": signal_asset_id},
                    style={"backgroundColor": "#FFC107", "width": "40px"},
                ).render(),
                width="auto",
            ),
            AlphaCol(
                AlphaButton(
                    "🗑️",
                    button_id={"type": "delete-config", "index": signal_asset_id},
                    style={"backgroundColor": "#DC3545", "width": "40px"},
                ).render(),
                width="auto",
            ),
        ]
    )


def build_table(uid: str) -> html.Table:
    configs = get_configs_by_uid(uid)

    headers = [
        "Signal Asset ID",
        "Platform Asset ID",
        "Entry Stagger",
        "Size Stagger",
        "# Staggers",
        "Size",
        "Decimals",
        "Actions",
    ]

    rows = [
        [
            c.signal_asset_id,
            c.platform_asset_id,
            c.entry_stagger_method,
            c.size_stagger_method,
            str(c.n_staggers),
            str(c.size),
            str(c.decimal_points),
            _action_buttons(c.signal_asset_id),
        ]
        for c in configs
    ]

    table = AlphaTable(table_id="details-table", headers=headers, rows=rows)

    return table.render()


# --- Page Class ---


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
                        AlphaButton(label="➕ Add Config", button_id="open-add-config-btn").render(),
                        AlphaModal(
                            modal_id="add-config-modal",
                            title="Add New Config",
                            body_content=_config_modal_fields("modal-add"),
                            confirm_id="confirm-add-config",
                            cancel_id="cancel-add-config",
                        ).render(),
                        AlphaModal(
                            modal_id="edit-config-modal",
                            title="Edit Config",
                            body_content=_config_modal_fields("modal-edit"),
                            confirm_id="confirm-edit-config",
                            cancel_id="cancel-edit-config",
                        ).render(),
                    ]
                ),
            ]
        )


page = SettingsDetailsPage("Settings Details")
layout = page.layout

# --- Callbacks ---


@callback(
    Output("settings-uid", "children"),
    Output("dynamic-header", "children"),
    Input("settings-url", "pathname"),
    prevent_initial_call=True,
)
def extract_uid_from_url(pathname: str):
    uid = pathname.split("/")[-1] if pathname else ""
    CoreLogger().debug(f"Extracted UID from URL: {uid}")

    account = get_account_by_uid(uid=uid)

    if not account:
        CoreLogger().error(f"Account with UID {uid} not found.")
        raise dash.exceptions.PreventUpdate

    return uid, PageHeader(f'Trade Settings for "{account.friendly_name}"')


@callback(
    Output("table-container", "children"),
    Input("settings-uid", "children"),
    prevent_initial_call=True,
)
def render_table(uid):
    return build_table(uid)


# --- Modal opening/canceling ---


@callback(
    Output("add-config-modal", "is_open"),
    [
        Input("open-add-config-btn", "n_clicks"),
        Input("confirm-add-config", "n_clicks"),
        Input("cancel-add-config", "n_clicks"),
    ],
    [State("add-config-modal", "is_open")],
    prevent_initial_call=True,
)
def toggle_add_modal(open_click, confirm_click, cancel_click, is_open):
    triggered = ctx.triggered_id
    if triggered == "open-add-config-btn":
        return True
    return False


@callback(
    Output("edit-config-modal", "is_open"),
    Output("modal-edit-signal-asset-id", "value"),
    Output("modal-edit-platform-asset-id", "value"),
    Output("modal-edit-entry-stagger", "value"),
    Output("modal-edit-size-stagger", "value"),
    Output("modal-edit-n-staggers", "value"),
    Output("modal-edit-size", "value"),
    Output("modal-edit-decimals", "value"),
    Input({"type": "edit-config", "index": ALL}, "n_clicks"),
    State("settings-uid", "children"),
    prevent_initial_call=True,
)
def open_edit_modal(edit_clicks, uid):
    if not any(edit_clicks):
        raise dash.exceptions.PreventUpdate

    triggered = ctx.triggered_id
    if not isinstance(triggered, dict) or triggered.get("type") != "edit-config":
        raise dash.exceptions.PreventUpdate

    signal_asset_id = triggered.get("index")
    config = next((c for c in get_configs_by_uid(uid) if c.signal_asset_id == signal_asset_id), None)
    if not config:
        raise dash.exceptions.PreventUpdate

    return (
        True,
        config.signal_asset_id,
        config.platform_asset_id,
        config.entry_stagger_method,
        config.size_stagger_method,
        config.n_staggers,
        config.size,
        config.decimal_points,
    )


# --- Confirming Save ---


@callback(
    Output("table-container", "children", allow_duplicate=True),
    Input("confirm-add-config", "n_clicks"),
    State("settings-uid", "children"),
    State("modal-add-signal-asset-id", "value"),
    State("modal-add-platform-asset-id", "value"),
    State("modal-add-entry-stagger", "value"),
    State("modal-add-size-stagger", "value"),
    State("modal-add-n-staggers", "value"),
    State("modal-add-size", "value"),
    State("modal-add-decimals", "value"),
    prevent_initial_call=True,
)
def save_new_config(_, uid, signal_id, platform_id, entry_stagger, size_stagger, n_staggers, size, decimals):
    if not signal_id or not platform_id:
        raise dash.exceptions.PreventUpdate

    upsert_config(
        uid,
        {
            "signal_asset_id": signal_id,
            "platform_asset_id": platform_id,
            "entry_stagger_method": entry_stagger,
            "size_stagger_method": size_stagger,
            "n_staggers": n_staggers,
            "size": size,
            "decimal_points": decimals,
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
    State("modal-edit-size-stagger", "value"),
    State("modal-edit-n-staggers", "value"),
    State("modal-edit-size", "value"),
    State("modal-edit-decimals", "value"),
    prevent_initial_call=True,
)
def save_edited_config(_, uid, signal_id, platform_id, entry_stagger, size_stagger, n_staggers, size, decimals):
    if not signal_id or not platform_id:
        raise dash.exceptions.PreventUpdate

    upsert_config(
        uid,
        {
            "signal_asset_id": signal_id,
            "platform_asset_id": platform_id,
            "entry_stagger_method": entry_stagger,
            "size_stagger_method": size_stagger,
            "n_staggers": n_staggers,
            "size": size,
            "decimal_points": decimals,
        },
    )

    return build_table(uid)


@callback(
    Output("table-container", "children", allow_duplicate=True),
    Input({"type": "delete-config", "index": ALL}, "n_clicks"),
    State("settings-uid", "children"),
    prevent_initial_call=True,
)
def handle_delete_config(delete_clicks, uid):
    triggered = ctx.triggered_id
    if not isinstance(triggered, dict) or triggered.get("type") != "delete-config":
        raise dash.exceptions.PreventUpdate

    if not any(delete_clicks):
        raise dash.exceptions.PreventUpdate

    signal_asset_id = triggered.get("index")
    delete_config(uid, signal_asset_id)

    return build_table(uid)
