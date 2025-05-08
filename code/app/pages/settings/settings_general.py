import dash
import dash_bootstrap_components as dbc
from dash import html, callback, Input, Output, State, ctx

from components.atoms.buttons.button import AlphaButton
from components.atoms.content import MainContent
from components.atoms.layout.layout import AlphaRow, AlphaCol
from components.atoms.modal.modal import AlphaModal
from components.atoms.table.table import AlphaTable
from components.atoms.text.page import PageHeader
from components.frame.body import PageBody
from pages.base_page import BasePage
from services.db.general_setting import get_all_settings, upsert_setting, delete_setting

dash.register_page(__name__, path="/settings/general", name="General Settings")

REQUIRED_KEYS = {"polygon_api_key"}


def _settings_modal_fields(prefix: str, key="", value=""):
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


def get_all_settings_with_required_defaults():
    settings = {s.key: s for s in get_all_settings()}
    for required_key in REQUIRED_KEYS:
        if required_key not in settings:
            upsert_setting(required_key, "")
            settings[required_key] = next(s for s in get_all_settings() if s.key == required_key)
    return list(settings.values())


def build_table():
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
                        style={"backgroundColor": "#FFC107", "width": "40px"},
                    ).render(),
                    width="auto",
                )
            ]
        )

        if setting.key not in REQUIRED_KEYS:
            actions.children.append(
                AlphaCol(
                    AlphaButton(
                        "🗑️",
                        {"type": "delete-setting", "index": setting.key},
                        style={"backgroundColor": "#DC3545", "width": "40px"},
                    ).render(),
                    width="auto",
                )
            )

        rows.append([setting.key, setting.value, actions])

    return AlphaTable(table_id="general-settings-table", headers=headers, rows=rows).render()


class GeneralSettingsPage(BasePage):
    def render(self):
        return PageBody(
            [
                PageHeader("General Settings").render(),
                MainContent(
                    [
                        build_table(),
                        html.Br(),
                        AlphaButton("➕ Add Setting", "open-add-setting-btn").render(),
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
def toggle_add_modal(open_click, confirm_click, cancel_click, is_open):
    return ctx.triggered_id == "open-add-setting-btn"


@callback(
    Output("edit-setting-modal", "is_open"),
    Output("modal-edit-key", "value"),
    Output("modal-edit-value", "value"),
    Input({"type": "edit-setting", "index": dash.ALL}, "n_clicks"),
    prevent_initial_call=True,
)
def open_edit_modal(edit_clicks):
    if not any(edit_clicks):
        raise dash.exceptions.PreventUpdate
    triggered = ctx.triggered_id
    key = triggered.get("index")
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
def save_new_setting(_, key, value):
    if not key or not value:
        raise dash.exceptions.PreventUpdate
    if key in (s.key for s in get_all_settings()):
        raise dash.exceptions.PreventUpdate  # prevent duplicate keys
    upsert_setting(key, value)
    return build_table()


@callback(
    Output("general-settings-table", "children", allow_duplicate=True),
    Input("confirm-edit-setting", "n_clicks"),
    State("modal-edit-key", "value"),
    State("modal-edit-value", "value"),
    prevent_initial_call=True,
)
def save_edited_setting(_, key, value):
    if not key:
        raise dash.exceptions.PreventUpdate
    upsert_setting(key, value)
    return build_table()


@callback(
    Output("general-settings-table", "children", allow_duplicate=True),
    Input({"type": "delete-setting", "index": dash.ALL}, "n_clicks"),
    prevent_initial_call=True,
)
def delete_selected_setting(_):
    triggered = ctx.triggered_id
    key = triggered.get("index")
    if key and key not in REQUIRED_KEYS:
        delete_setting(key)
    return build_table()
