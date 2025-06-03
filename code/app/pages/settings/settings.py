from typing import List, Tuple

import dash
import dash_bootstrap_components as dbc
from components.atoms.buttons.general.button import AlphaButton
from components.atoms.content import MainContent
from components.atoms.divider.divider import Divider
from components.atoms.layout.layout import AlphaCol, AlphaRow
from components.atoms.modal.modal import AlphaModal
from components.atoms.table.table import AlphaTable
from components.atoms.text.page import PageHeader
from components.frame.body import PageBody
from dash import Input, Output, State, callback, ctx, html
from models.main.general_setting import GeneralSetting
from pages.base_page import BasePage
from quant_core.services.core_logger import CoreLogger
from services.db.cache.trade_history import sync_trades_from_all_accounts
from services.db.main.general_setting import delete_setting, get_all_settings, upsert_setting

dash.register_page(__name__, path="/settings", name="Settings")

_REQUIRED_KEYS = {"polygon_api_key"}


def _settings_modal_fields(prefix: str, key: str = "", value: str = "") -> html.Div:
    return html.Div(
        [
            dbc.Input(
                id=f"{prefix}-key",
                value=key,
                placeholder="Setting Key",
                className="mb-2",
                disabled=(prefix == "modal-edit"),
            ),
            dbc.Input(id=f"{prefix}-value", value=value, placeholder="Setting Value", className="mb-2"),
        ]
    )


def get_all_settings_with_required_defaults() -> List[GeneralSetting]:
    """Return all settings, ensuring required keys are present."""
    settings = {setting.key: setting for setting in get_all_settings()}
    for required_key in _REQUIRED_KEYS:
        if required_key not in settings:
            upsert_setting(required_key, "")
            settings[required_key] = next(setting for setting in get_all_settings() if setting.key == required_key)

    return list(settings.values())


def build_table() -> html.Table:
    """Build the settings table with all settings and their actions."""
    settings = get_all_settings_with_required_defaults()
    headers = ["Key", "Value", "Actions"]
    rows = []

    for setting in settings:
        actions = AlphaRow(
            [
                AlphaCol(
                    AlphaButton(
                        "✏️",
                        {"type": "edit-setting", "index": setting.key},
                    ).render(),
                    width="auto",
                )
            ]
        )

        if setting.key not in _REQUIRED_KEYS:
            actions.children.append(
                AlphaCol(
                    AlphaButton(
                        "🗑️",
                        {"type": "delete-setting", "index": setting.key},
                    ).render(),
                    width="auto",
                )
            )

        rows.append([setting.key, setting.value, actions])

    return AlphaTable(table_id="general-settings-table", headers=headers, rows=rows).render()


class GeneralSettingsPage(BasePage):  # pylint: disable=too-few-public-methods
    """General Settings Page."""

    def render(self):
        """Render the page layout."""
        return PageBody(
            [
                PageHeader("Settings").render(),
                MainContent(
                    [
                        build_table(),
                        Divider().render(),
                        AlphaButton("➕ Add Setting", "open-add-setting-btn").render(),
                        Divider().render(),
                        Divider().render(),
                        AlphaButton("🔄 Sync Trades from TradingView", "sync-trades-btn").render(),
                        html.Div(id="sync-trades-status", className="mt-3"),
                        AlphaModal(
                            modal_id="add-setting-modal",
                            title="Add Setting",
                            body_content=_settings_modal_fields("modal-add"),
                            confirm_id="confirm-add-setting",
                            cancel_id="cancel-add-setting",
                        ).render(),
                        AlphaModal(
                            modal_id="edit-setting-modal",
                            title="Edit Setting",
                            body_content=_settings_modal_fields("modal-edit"),
                            confirm_id="confirm-edit-setting",
                            cancel_id="cancel-edit-setting",
                        ).render(),
                    ]
                ),
            ]
        )


page = GeneralSettingsPage("General Settings")
layout = page.layout


@callback(
    Output("add-setting-modal", "is_open"),
    [
        Input("open-add-setting-btn", "n_clicks"),
        Input("confirm-add-setting", "n_clicks"),
        Input("cancel-add-setting", "n_clicks"),
    ],
    State("add-setting-modal", "is_open"),
    prevent_initial_call=True,
)
def toggle_add_modal(_, __, ___, ____) -> bool:
    """Toggle the add setting modal."""
    return ctx.triggered_id == "open-add-setting-btn"


@callback(
    Output("edit-setting-modal", "is_open"),
    Output("modal-edit-key", "value"),
    Output("modal-edit-value", "value"),
    Input({"type": "edit-setting", "index": dash.ALL}, "n_clicks"),
    prevent_initial_call=True,
)
def open_edit_modal(edit_clicks: List[int]) -> Tuple[bool, str, str]:
    """Open the edit modal and populate it with the selected setting's key and value."""
    if not any(edit_clicks):
        raise dash.exceptions.PreventUpdate

    key = ctx.triggered_id.get("index")
    setting = next((s for s in get_all_settings() if s.key == key), None)

    if not setting:
        raise dash.exceptions.PreventUpdate

    return True, setting.key, setting.value


@callback(
    Output("general-settings-table", "children", allow_duplicate=True),
    Input("confirm-add-setting", "n_clicks"),
    State("modal-add-key", "value"),
    State("modal-add-value", "value"),
    prevent_initial_call=True,
)
def save_new_setting(_, key: str, value: str) -> html.Table:
    """Save new setting to the database."""
    if not key or not value:
        raise dash.exceptions.PreventUpdate
    if key in (s.key for s in get_all_settings()):
        raise dash.exceptions.PreventUpdate
    upsert_setting(key, value)

    return build_table()


@callback(
    Output("general-settings-table", "children", allow_duplicate=True),
    Input("confirm-edit-setting", "n_clicks"),
    State("modal-edit-key", "value"),
    State("modal-edit-value", "value"),
    prevent_initial_call=True,
)
def save_edited_setting(_, key: str, value: str) -> html.Table:
    """Save edited setting to the database."""
    if not key:
        raise dash.exceptions.PreventUpdate
    upsert_setting(key, value)

    return build_table()


@callback(
    Output("general-settings-table", "children", allow_duplicate=True),
    Input({"type": "delete-setting", "index": dash.ALL}, "n_clicks"),
    prevent_initial_call=True,
)
def delete_selected_setting(_) -> html.Table:
    """Delete selected setting if it's not required."""
    key = ctx.triggered_id.get("index")
    if key and key not in _REQUIRED_KEYS:
        delete_setting(key)

    return build_table()


@callback(
    Output("sync-trades-status", "children"),
    Input("sync-trades-btn", "n_clicks"),
    prevent_initial_call=True,
)
def sync_trades_from_metatrader_5(_) -> dbc.Alert:
    """Sync Trades from MetaTrader 5 and store them in the database."""
    try:
        result = sync_trades_from_all_accounts()
        CoreLogger().info("Successfully synced trades from MetaTrader.")
        return dbc.Alert(f"✅ Synced trades: {result}", color="success", dismissable=True)
    except Exception as error:  # pylint: disable=broad-exception-caught
        CoreLogger().error(f"During sync trades from MetaTrader the following error occured: {str(error)}")
        return dbc.Alert(f"❌ Sync failed: {str(error)}", color="danger", dismissable=True)
