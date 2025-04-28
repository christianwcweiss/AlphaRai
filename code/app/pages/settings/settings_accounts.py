import random
import string
from typing import Optional

import dash
import dash_bootstrap_components as dbc
from dash import html, Input, Output, State, ctx, dcc, callback, ALL
from dash.exceptions import PreventUpdate

from components.atoms.buttons.button import AlphaButton
from components.atoms.card.card import AlphaCard
from components.atoms.content import MainContent
from components.atoms.layout.layout import AlphaRow, AlphaCol
from components.atoms.text.page import PageHeader
from components.atoms.text.section import SectionHeader
from components.frame.body import PageBody
from constants import colors
from pages.base_page import BasePage
from quant_core.enums.platform import Platform
from services.db.accounts import (
    get_all_accounts,
    upsert_account,
    delete_account,
)

dash.register_page(__name__, path="/settings/accounts", name="Account Settings")

# ===


def generate_uid(length: int = 8) -> str:
    return "".join(random.choices(string.ascii_uppercase + string.digits, k=length))


def render_account_card(
    platform: Platform, label: str = "", secret_name: str = "", idx: int = 0, uid: Optional[str] = None
) -> html.Div:
    uid = uid or generate_uid()
    delete_id = {"type": f"{platform.value.lower()}-delete", "index": uid}

    return AlphaCard(
        title=label if label else "New Account",
        children=[
            html.Div(
                AlphaRow(
                    [
                        AlphaCol(
                            AlphaButton(
                                label="🗑️ Delete",
                                button_id=delete_id,
                                style={"backgroundColor": colors.ERROR_COLOR},
                            ).render(),
                            xs=12,
                            sm=12,
                            md=12,
                            lg=6,
                            xl=6,
                        ),
                        AlphaCol(
                            AlphaButton(
                                label="⚙️ Config",
                                href=f"/settings/accounts/{uid}",
                                style={"backgroundColor": colors.SECONDARY_COLOR},
                            ).render(),
                            xs=12,
                            sm=12,
                            md=12,
                            lg=6,
                            xl=6,
                        ),
                    ]
                )
            )
        ],
    ).render()


# ===


class SettingsPage(BasePage):
    def render(self):
        return PageBody(
            [
                html.Div(id="page-init", style={"display": "none"}),
                PageHeader("Settings"),
                MainContent(
                    [
                        SectionHeader(title="Accounts", subtitle="Manage your Accounts").render(),
                        dcc.Loading(
                            id="loading-accounts",
                            type="circle",
                            children=html.Div(id="mt5-rows", style={"marginTop": "20px"}),
                        ),
                        AlphaButton(label="➕ Add MT5 Account", button_id="open-add-mt5-btn").render(),
                        dbc.Modal(
                            id="add-account-modal",
                            is_open=False,
                            children=[
                                dbc.ModalHeader(dbc.ModalTitle("➕ Add New MT5 Account")),
                                dbc.ModalBody(
                                    [
                                        dbc.Input(
                                            id="input-account-name",
                                            placeholder="Friendly Name",
                                            type="text",
                                            className="mb-2",
                                        ),
                                        dbc.Input(
                                            id="input-account-secret", placeholder="AWS Secret Name", type="text"
                                        ),
                                    ]
                                ),
                                dbc.ModalFooter(
                                    [
                                        dbc.Button("Save", id="confirm-add-account", color="success"),
                                        dbc.Button(
                                            "Cancel", id="close-add-account", color="secondary", className="ms-2"
                                        ),
                                    ]
                                ),
                            ],
                        ),
                        html.Hr(),
                    ]
                ),
            ]
        )


page = SettingsPage("Settings")
layout = page.layout

# ===

# --- Callbacks ---


@callback(
    Output("add-account-modal", "is_open"),
    [
        Input("open-add-mt5-btn", "n_clicks"),
        Input("close-add-account", "n_clicks"),
        Input("confirm-add-account", "n_clicks"),
    ],
    [State("add-account-modal", "is_open")],
    prevent_initial_call=True,
)
def toggle_add_modal(open_click, close_click, save_click, is_open):
    triggered = ctx.triggered_id
    if triggered == "open-add-mt5-btn":
        return True
    elif triggered in ["close-add-account", "confirm-add-account"]:
        return False
    return is_open


@callback(
    Output("mt5-rows", "children", allow_duplicate=True),
    Input("confirm-add-account", "n_clicks"),
    State("input-account-name", "value"),
    State("input-account-secret", "value"),
    prevent_initial_call=True,
)
def save_new_account(_, label, secret):
    if not label or not secret:
        raise PreventUpdate

    upsert_account(Platform.METATRADER.value, label, secret, generate_uid(8))
    return reload_mt5_accounts()


@callback(
    Output("mt5-rows", "children", allow_duplicate=True),
    Input("page-init", "children"),
    prevent_initial_call="initial_duplicate",
)
def load_mt5_credentials_on_page_load(_):
    return reload_mt5_accounts()


@callback(
    Output("mt5-rows", "children", allow_duplicate=True),
    Input({"type": "metatrader-delete", "index": ALL}, "n_clicks"),
    State({"type": "metatrader-delete", "index": ALL}, "id"),
    prevent_initial_call=True,
)
def handle_delete_account(delete_clicks, button_ids):
    if not delete_clicks or not button_ids:
        raise PreventUpdate

    for n_clicks, button_id in zip(delete_clicks, button_ids):
        if n_clicks:  # Only if a button was actually clicked
            uid_to_delete = button_id["index"]
            delete_account(Platform.METATRADER.value, uid_to_delete)
            break  # Delete only one per click

    return reload_mt5_accounts()


# ===


def reload_mt5_accounts():
    credentials = [c for c in get_all_accounts() if Platform(c.platform.upper()) is Platform.METATRADER]
    return AlphaRow(
        [
            AlphaCol(
                render_account_card(Platform.METATRADER, c.friendly_name, c.secret_name, idx=i, uid=c.uid),
                xs=12,
                sm=6,
                md=4,
                lg=3,
                xl=3,
            )
            for i, c in enumerate(credentials)
        ]
    )
