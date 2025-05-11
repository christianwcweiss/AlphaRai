import random
import string

import dash
import dash_bootstrap_components as dbc
import pandas as pd
from dash import html, dcc, Input, Output, State, ctx, callback, MATCH, ALL
from dash.exceptions import PreventUpdate
import plotly.graph_objects as go

from quant_core.metrics.account_balance_over_time.relative.balance_over_time import AccountBalanceOverTimeRelative
from services.db.account_config import get_configs_by_account_id
from services.db.trade_history import get_all_trades

from components.atoms.buttons.general.button import AlphaButton
from components.atoms.content import MainContent
from components.atoms.layout.layout import AlphaRow, AlphaCol
from components.atoms.text.page import PageHeader
from components.atoms.text.section import SectionHeader
from components.frame.body import PageBody
from components.molecules.cards.settings.account_card import AccountSettingsCard
from pages.base_page import BasePage
from quant_core.enums.platform import Platform
from services.db.account import (
    get_all_accounts,
    upsert_account,
    delete_account,
)


# Register page
dash.register_page(__name__, path="/settings/accounts", name="Account Settings")


def generate_uid(length: int = 8) -> str:
    return "".join(random.choices(string.ascii_uppercase + string.digits, k=length))


def render_account_card(account, rel_df):
    configs = get_configs_by_account_id(account.id)
    total = len(configs)
    enabled = sum(1 for c in configs if c.enabled)
    df = rel_df[rel_df["account_id"] == account.id] if not rel_df.empty else None
    return AccountSettingsCard(account, enabled, total, df).render()


def reload_mt5_accounts():
    accounts = [account for account in get_all_accounts() if Platform(account.platform.upper()) is Platform.METATRADER]
    accounts = sorted(accounts, key=lambda x: x.friendly_name)
    trades = get_all_trades()
    df = pd.DataFrame([t.__dict__ for t in trades]) if trades else pd.DataFrame()

    if not df.empty:
        df = df[[col for col in df.columns if not col.startswith("_sa_")]]
        metric = AccountBalanceOverTimeRelative()
        rel_df = metric.calculate_grouped(df)
    else:
        rel_df = pd.DataFrame()

    return AlphaRow([
        AlphaCol(render_account_card(account, rel_df), xs=12, sm=6, md=4, lg=3, xl=3)
        for account in accounts
    ])


class SettingsPage(BasePage):
    def render(self):
        return PageBody(
            [
                html.Div(id="page-init", children="trigger", style={"display": "none"}),
                PageHeader("Settings").render(),
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
                                        dbc.Button("Cancel", id="close-add-account", color="secondary", className="ms-2"),
                                    ]
                                ),
                            ],
                        ),
                        dcc.Store(id="pending-delete-uid"),
                        dbc.Modal(
                            id="delete-confirm-modal",
                            is_open=False,
                            children=[
                                dbc.ModalHeader("Confirm Deletion"),
                                dbc.ModalBody("Are you sure you want to delete this account?"),
                                dbc.ModalFooter([
                                    dbc.Button("Delete", id="confirm-delete-btn", color="danger"),
                                    dbc.Button("Cancel", id="cancel-delete-btn", color="secondary", className="ms-2"),
                                ]),
                            ],
                        ),
                        html.Hr(),
                    ]
                ),
            ]
        )


page = SettingsPage("Settings")
layout = page.layout


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
    Output("delete-confirm-modal", "is_open", allow_duplicate=True),
    Output("pending-delete-uid", "data", allow_duplicate=True),
    [
        Input({"type": "initiate-delete", "index": ALL}, "n_clicks"),
        Input("cancel-delete-btn", "n_clicks"),
        Input("confirm-delete-btn", "n_clicks"),
    ],
    [
        State("pending-delete-uid", "data"),
        State({"type": "initiate-delete", "index": ALL}, "id"),
    ],
    prevent_initial_call=True,
)
def manage_delete(_, cancel_click, confirm_click, pending_uid, ids):
    triggered = ctx.triggered_id

    # Cancel
    if triggered == "cancel-delete-btn":
        return dash.no_update, False, dash.no_update

    # Confirm deletion
    elif triggered == "confirm-delete-btn":
        if pending_uid:
            delete_account(Platform.METATRADER.value, pending_uid)
            return reload_mt5_accounts(), False, None
        else:
            raise PreventUpdate

    # Open modal
    elif isinstance(triggered, dict) and triggered.get("type") == "initiate-delete":
        return dash.no_update, True, triggered["index"]

    raise PreventUpdate
