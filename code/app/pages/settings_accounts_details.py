from typing import Optional

import dash
import dash_bootstrap_components as dbc
from dash import html, Input, Output, State, ctx, callback, dcc, ALL

from components.atoms.content import MainContent
from components.atoms.text.page import PageHeader
from components.frame.body import PageBody
from components.atoms.table.row import AlphaRow
from components.atoms.table.table import AlphaTable
from pages.base_page import BasePage
from quant_core.enums.stagger_method import StaggerMethod
from quant_core.services.core_logger import CoreLogger
from services.accounts import get_account_by_uid

from services.trade_config import get_configs_by_uid, upsert_config, delete_config


dash.register_page(__name__, path_template="/settings/accounts/<uid>", name="Account Settings Details")

SIGNAL_ID_WIDTH = 1
PLATFORM_ID_WIDTH = 1
ENTRY_STAGGER_WIDTH = 2
SIZE_STAGGER_WIDTH = 2
N_STAGGERS_WIDTH = 1
SIZE_WIDTH = 2
DECIMALS_WIDTH = 1
DELETE_WIDTH = 1


def render_header_row() -> AlphaRow:
    return AlphaRow(
        [
            dbc.Col(html.Label("Signal Asset ID"), width=SIGNAL_ID_WIDTH),
            dbc.Col(html.Label("Platform Asset ID"), width=PLATFORM_ID_WIDTH),
            dbc.Col(html.Label("Entry Stagger"), width=ENTRY_STAGGER_WIDTH),
            dbc.Col(html.Label("Size Stagger"), width=SIZE_STAGGER_WIDTH),
            dbc.Col(html.Label("# Staggers"), width=N_STAGGERS_WIDTH),
            dbc.Col(html.Label("Size"), width=SIZE_WIDTH),
            dbc.Col(html.Label("Decimals"), width=DECIMALS_WIDTH),
            dbc.Col(html.Label("Delete"), width=DELETE_WIDTH),
        ],
        id="details-header",
    )


def render_config_row(
    uid: str,
    idx: int = 0,
    signal_asset_id: str = "",
    platform_asset_id: str = "",
    entry_stagger: Optional[str] = None,
    size_stagger: Optional[str] = None,
    n_staggers: int = 1,
    size: float = 0.0,
    decimal_points: int = 2,
) -> AlphaRow:
    select_entry = dbc.Select(
        id={"type": "entry-stagger", "index": idx},
        options=[{"label": m.value.capitalize(), "value": m.value} for m in StaggerMethod],
        value=entry_stagger or StaggerMethod.LINEAR.value,
    )
    select_size = dbc.Select(
        id={"type": "size-stagger", "index": idx},
        options=[{"label": m.value.capitalize(), "value": m.value} for m in StaggerMethod],
        value=size_stagger or StaggerMethod.LINEAR.value,
    )

    return AlphaRow(
        [
            dbc.Col(dbc.Input(value=signal_asset_id, id={"type": "signal-asset", "index": idx}), width=SIGNAL_ID_WIDTH),
            dbc.Col(
                dbc.Input(value=platform_asset_id, id={"type": "platform-asset", "index": idx}), width=PLATFORM_ID_WIDTH
            ),
            dbc.Col(select_entry, width=ENTRY_STAGGER_WIDTH),
            dbc.Col(select_size, width=SIZE_STAGGER_WIDTH),
            dbc.Col(
                dbc.Input(type="number", value=n_staggers, id={"type": "n-staggers", "index": idx}, min=1),
                width=N_STAGGERS_WIDTH,
            ),
            dbc.Col(
                dbc.Input(type="number", value=size, id={"type": "size", "index": idx}, step=0.01, min=0.01),
                width=SIZE_WIDTH,
            ),
            dbc.Col(
                dbc.Input(type="number", value=decimal_points, id={"type": "decimals", "index": idx}, min=0, step=1),
                width=DECIMALS_WIDTH,
            ),
            dbc.Col(
                dbc.Button("🗑️", id={"type": "delete-config", "index": idx}, color="danger", size="sm"),
                width=DELETE_WIDTH,
            ),
        ],
        id={"type": "details-row", "index": idx},
    )


class SettingsDetailsPage(BasePage):
    def render(self):
        return PageBody(
            [
                dcc.Location(id="settings-url"),
                html.Div(id="settings-uid", style={"display": "none"}),
                html.Div(id="page-init", style={"display": "none"}),
                html.Div(id="dynamic-header"),
                MainContent(
                    [
                        AlphaTable(table_id="details-table", header_row=render_header_row(), rows=[]),
                        dbc.Button("Add Config", id="add-config", size="sm", color="secondary", className="mb-3"),
                        html.Div(id="details-status", className="mt-2"),
                        dbc.Button("Save Settings", id="save-details", color="success", className="mt-3"),
                    ]
                ),
            ]
        )


page = SettingsDetailsPage("Settings Details")
layout = page.layout


@callback(
    Output("details-table", "children", allow_duplicate=True),
    Input("page-init", "children"),
    Input("settings-uid", "children"),
    prevent_initial_call="initial_duplicate",
)
def load_existing_config_rows(_, uid: str):
    CoreLogger().info("Loading existing settings details table")
    configs = get_configs_by_uid(uid.upper())
    CoreLogger().debug(f"Loaded {len(configs)} configs for UID: {uid}")
    CoreLogger().debug(f"Configs: {configs}")

    rows = [render_header_row()]
    if not configs:
        return rows

    for i, c in enumerate(configs):
        rows.append(
            render_config_row(
                uid=uid,
                idx=i,
                signal_asset_id=c.signal_asset_id,
                platform_asset_id=c.platform_asset_id,
                entry_stagger=c.entry_stagger_method,
                size_stagger=c.size_stagger_method,
                n_staggers=c.n_staggers,
                size=c.size,
                decimal_points=c.decimal_points,
            )
        )

    return rows


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

    return uid, PageHeader(f"Trade Settings for {account.friendly_name}")


@callback(
    Output("details-table", "children"),
    Input("add-config", "n_clicks"),
    Input({"type": "delete-config", "index": ALL}, "n_clicks"),
    Input({"type": "signal-asset", "index": ALL}, "value"),
    Input({"type": "platform-asset", "index": ALL}, "value"),
    Input({"type": "entry-stagger", "index": ALL}, "value"),
    Input({"type": "size-stagger", "index": ALL}, "value"),
    Input({"type": "n-staggers", "index": ALL}, "value"),
    Input({"type": "size", "index": ALL}, "value"),
    Input({"type": "decimals", "index": ALL}, "value"),
    State("settings-uid", "children"),
    prevent_initial_call=True,
)
def handle_config_modifications(
    add_clicks, delete_clicks, signal_ids, platform_ids, entry_staggers, size_staggers, n_staggers, sizes, decimals, uid
):
    triggered = ctx.triggered_id
    rows = list(zip(signal_ids, platform_ids, entry_staggers, size_staggers, n_staggers, sizes, decimals))

    if isinstance(triggered, dict) and triggered.get("type") == "delete-config":
        index = triggered["index"]
        rows.pop(index)
    elif triggered == "add-config":
        rows.append(("", "", StaggerMethod.LINEAR.value, StaggerMethod.LINEAR.value, 1, 0.0, 2))

    return [render_header_row()] + [
        render_config_row(
            uid,
            idx=i,
            signal_asset_id=r[0],
            platform_asset_id=r[1],
            entry_stagger=r[2],
            size_stagger=r[3],
            n_staggers=r[4],
            size=r[5],
            decimal_points=r[6],
        )
        for i, r in enumerate(rows)
    ]


@callback(
    Output("details-status", "children"),
    Input("save-details", "n_clicks"),
    State("settings-uid", "children"),
    State({"type": "signal-asset", "index": ALL}, "value"),
    State({"type": "platform-asset", "index": ALL}, "value"),
    State({"type": "entry-stagger", "index": ALL}, "value"),
    State({"type": "size-stagger", "index": ALL}, "value"),
    State({"type": "n-staggers", "index": ALL}, "value"),
    State({"type": "size", "index": ALL}, "value"),
    State({"type": "decimals", "index": ALL}, "value"),
    prevent_initial_call=True,
)
def save_settings(_, uid, signal_ids, platform_ids, entry_staggers, size_staggers, n_staggers, sizes, decimals):
    submitted = [
        {
            "signal_asset_id": s,
            "platform_asset_id": p,
            "entry_stagger_method": e,
            "size_stagger_method": ss,
            "n_staggers": n,
            "size": sz,
            "decimal_points": d,
        }
        for s, p, e, ss, n, sz, d in zip(
            signal_ids, platform_ids, entry_staggers, size_staggers, n_staggers, sizes, decimals
        )
        if s and p
    ]

    existing = get_configs_by_uid(uid)
    existing_ids = {cfg.signal_asset_id for cfg in existing}
    submitted_ids = {c["signal_asset_id"] for c in submitted}

    for config in submitted:
        upsert_config(uid, config)

    for old_id in existing_ids - submitted_ids:
        delete_config(uid, old_id)

    return dbc.Alert("Settings saved successfully!", color="success", dismissable=True)
