import random
import string
from typing import Optional

import dash
import dash_bootstrap_components as dbc
from dash import html, Input, Output, ALL, callback, ctx, State, dcc

from components.atoms.content import MainContent
from components.atoms.text.page import PageHeader
from components.atoms.text.section import SectionHeader
from components.atoms.table.row import AlphaRow
from components.atoms.table.table import AlphaTable
from components.frame.body import PageBody
from pages.base_page import BasePage
from quant_core.enums.platform import Platform
from services.db.accounts import (
    get_all_accounts,
    upsert_account,
    delete_account,
)

dash.register_page(__name__, path="/settings/accounts", name="Account Settings")

TOOLTIP_HINT = "This is the AWS Secrets Manager name, e.g. MT5_SECRET_EU"


def generate_uid(length: int = 8) -> str:
    return "".join(random.choices(string.ascii_uppercase + string.digits, k=length))


def render_header_row() -> AlphaRow:
    return AlphaRow(
        [
            dbc.Col(html.Label("Name"), width=4),
            dbc.Col(html.Label("AWS Secret Name"), width=6),
            dbc.Col(html.Label("Delete"), width=1),
            dbc.Col(html.Label("Config"), width=1),
        ],
        id="header-row",
    )


def render_account_row(
    platform: Platform, label: str = "", secret_name: str = "", idx: int = 0, uid: Optional[str] = None
) -> AlphaRow:
    uid = uid or generate_uid()
    label_id = {"type": f"{platform.value.lower()}-label", "index": idx}
    secret_id = {"type": f"{platform.value.lower()}-secret", "index": idx}
    delete_id = {"type": f"{platform.value.lower()}-delete", "index": idx}
    settings_link = dcc.Link("⚙️", href=f"/settings/accounts/{uid}")

    return AlphaRow(
        [
            dbc.Col(dbc.Input(id=label_id, value=label, placeholder="Name (e.g. 'Demo EU')"), width=4),
            dbc.Col(dbc.Input(id=secret_id, value=secret_name, placeholder="AWS Secret Name"), width=6),
            dbc.Col(dbc.Button("🗑️", id=delete_id, color="danger", size="sm"), width=1),
            dbc.Col(settings_link, width=1),
            html.Div(uid, id={"type": f"{platform.value.lower()}-uid", "index": idx}, style={"display": "none"}),
        ],
        id={"type": f"{platform.value.lower()}-row", "index": idx},
    )


class SettingsPage(BasePage):
    def render(self):
        return PageBody(
            [
                html.Div(id="page-init", style={"display": "none"}),  # Triggers page load
                PageHeader("Settings"),
                MainContent(
                    [
                        SectionHeader(title="Metatrader5 Accounts", subtitle="Manage your MT5 accounts").render(),
                        AlphaTable(table_id="mt5-rows", header_row=render_header_row(), rows=[]),
                        dbc.Button("Add MT5 Account", id="add-mt5-btn", size="sm", color="secondary", className="mb-3"),
                        SectionHeader(title="IG Accounts", subtitle="Manage your IG accounts").render(),
                        AlphaTable(table_id="ig-rows", header_row=render_header_row(), rows=[]),
                        dbc.Button("Add IG Account", id="add-ig-btn", size="sm", color="secondary", className="mb-3"),
                        html.Hr(),
                        dbc.Button("Save Settings", id="save-settings", color="success", className="mt-3"),
                        html.Div(id="save-status", className="mt-2"),
                    ]
                ),
            ]
        )


page = SettingsPage("Settings")
layout = page.layout


@callback(
    Output("mt5-rows", "children"),
    Input("add-mt5-btn", "n_clicks"),
    Input({"type": "metatrader-delete", "index": ALL}, "n_clicks"),
    Input({"type": "metatrader-label", "index": ALL}, "value"),
    Input({"type": "metatrader-secret", "index": ALL}, "value"),
    Input({"type": "metatrader-uid", "index": ALL}, "children"),
    prevent_initial_call=True,
)
def handle_mt5_modifications(add_clicks, delete_clicks, labels, secrets, uids):
    triggered = ctx.triggered_id
    rows = list(zip(labels, secrets, uids))

    if isinstance(triggered, dict) and triggered.get("type") == "metatrader-delete":
        index = triggered.get("index")
        rows.pop(index)

    elif triggered == "add-mt5-btn":
        rows.append(("", "", generate_uid()))

    return [render_account_row(Platform.METATRADER, l, s, idx=i, uid=u) for i, (l, s, u) in enumerate(rows)]


@callback(
    Output("mt5-rows", "children", allow_duplicate=True),
    Input("page-init", "children"),
    prevent_initial_call="initial_duplicate",
)
def load_mt5_credentials_on_page_load(_):
    credentials = [c for c in get_all_accounts() if Platform(c.platform.upper()) is Platform.METATRADER]
    return [
        render_account_row(Platform.METATRADER, c.friendly_name, c.secret_name, idx=i, uid=c.uid)
        for i, c in enumerate(credentials)
    ]


@callback(
    Output("ig-rows", "children"),
    Input("add-ig-btn", "n_clicks"),
    Input({"type": "ig-delete", "index": ALL}, "n_clicks"),
    Input({"type": "ig-label", "index": ALL}, "value"),
    Input({"type": "ig-secret", "index": ALL}, "value"),
    Input({"type": "ig-uid", "index": ALL}, "children"),
    prevent_initial_call=True,
)
def handle_ig_modifications(add_clicks, delete_clicks, labels, secrets, uids):
    triggered = ctx.triggered_id
    rows = list(zip(labels, secrets, uids))

    if isinstance(triggered, dict) and triggered.get("type") == "ig-delete":
        index = triggered.get("index")
        rows.pop(index)

    elif triggered == "add-ig-btn":
        rows.append(("", "", generate_uid()))

    return [render_account_row(Platform.IG, l, s, idx=i, uid=u) for i, (l, s, u) in enumerate(rows)]


@callback(
    Output("ig-rows", "children", allow_duplicate=True),
    Input("page-init", "children"),
    prevent_initial_call="initial_duplicate",
)
def load_ig_credentials_on_page_load(_):
    credentials = [c for c in get_all_accounts() if Platform(c.platform.upper()) is Platform.IG]
    return [
        render_account_row(Platform.IG, c.friendly_name, c.secret_name, idx=i, uid=c.uid)
        for i, c in enumerate(credentials)
    ]


@callback(
    Output("save-status", "children"),
    Input("save-settings", "n_clicks"),
    State({"type": "metatrader-label", "index": ALL}, "value"),
    State({"type": "metatrader-secret", "index": ALL}, "value"),
    State({"type": "metatrader-uid", "index": ALL}, "children"),
    State({"type": "ig-label", "index": ALL}, "value"),
    State({"type": "ig-secret", "index": ALL}, "value"),
    State({"type": "ig-uid", "index": ALL}, "children"),
    prevent_initial_call=True,
)
def save_all_credentials(_, mt5_labels, mt5_secrets, mt5_uids, ig_labels, ig_secrets, ig_uids):
    mt5_submitted = [
        dict(label=l, secret=s, uid=u) for l, s, u in zip(mt5_labels, mt5_secrets, mt5_uids) if l and s and u
    ]
    ig_submitted = [dict(label=l, secret=s, uid=u) for l, s, u in zip(ig_labels, ig_secrets, ig_uids) if l and s and u]

    all_existing = get_all_accounts()
    mt5_existing_uids = {s.uid for s in all_existing if Platform(s.platform.upper()) is Platform.METATRADER}
    ig_existing_uids = {s.uid for s in all_existing if Platform(s.platform.upper()) is Platform.IG}

    for row in mt5_submitted:
        upsert_account(Platform.METATRADER.value, row["label"], row["secret"], row["uid"])
    for old_uid in mt5_existing_uids - {r["uid"] for r in mt5_submitted}:
        delete_account(Platform.METATRADER.value, old_uid)

    for row in ig_submitted:
        upsert_account(Platform.IG.value, row["label"], row["secret"], row["uid"])
    for old_uid in ig_existing_uids - {r["uid"] for r in ig_submitted}:
        delete_account(Platform.IG.value, old_uid)

    return dbc.Alert("Credentials saved successfully!", color="success", dismissable=True)
