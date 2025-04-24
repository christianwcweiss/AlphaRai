import os
import uuid
import dash
import dash_bootstrap_components as dbc
from dash import html, dcc, callback, Input, Output, State, ctx

from components.atoms.content import MainContent
from components.atoms.text.page import PageHeader
from components.atoms.text.section import SectionHeader
from components.atoms.text.subsection import SubsectionHeader
from components.frame.body import PageBody
from pages.base_page import BasePage
from quant_core.services.core_logger import CoreLogger

from services.strategy_discovery import discover_strategies
from services.strategy import (
    get_all_registered_strategy_ids,
    register_strategy,
    unregister_strategy,
)

STRATEGY_FOLDER = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", "strategies"))

dash.register_page(__name__, path="/strategies", name="Strategies")


class StrategiesPage(BasePage):
    def render(self):
        return PageBody(
            [
                PageHeader(f"{self._title}"),
                MainContent(
                    [
                        dcc.Store(id="refresh-strategies", data=str(uuid.uuid4())),
                        html.Div(id="strategy-lists"),
                        html.Div(id="strategy-register-output", style={"marginTop": "1em"}),
                    ]
                ),
            ]
        )


page = StrategiesPage(title="Strategies")
layout = page.layout


@callback(Output("strategy-lists", "children"), Input("refresh-strategies", "data"))
def render_strategy_lists(_):
    all_strategies = discover_strategies(STRATEGY_FOLDER)

    try:
        registered_ids = get_all_registered_strategy_ids()
    except Exception as e:
        return dbc.Alert(f"⚠️ DB error: {e}", color="danger", dismissable=True)

    registered = []
    unregistered = []

    for s in all_strategies:
        if s["id"] in registered_ids:
            registered.append(s)
        else:
            unregistered.append(s)

    def strategy_card(s, registered=True):
        color = "success" if registered else "danger"
        label = "Unregister" if registered else "Register"
        button_id = {"type": "unregister-btn" if registered else "register-btn", "index": s["id"]}

        return dbc.Card(
            dbc.CardBody(
                [
                    dcc.Link(
                        html.Div([html.Strong(s["id"]), html.Small(f" ({s['type']})", className="ms-1")]),
                        href=f"/strategies/{s['id']}",
                        style={"color": "inherit", "textDecoration": "none"},
                    ),
                    dbc.Button(label, id=button_id, color="light", size="sm", className="mt-2"),
                ]
            ),
            className=f"m-2 border border-{color} bg-{color} text-white rounded-3",
            style={"width": "170px", "display": "inline-block", "textAlign": "center"},
        )

    return html.Div(
        [
            SectionHeader("Strategy Management", subtitle="Register/Unregister strategies").render(),
            SubsectionHeader("Registered Strategies"),
            html.Div([strategy_card(s, registered=True) for s in registered]),
            html.Hr(),
            SubsectionHeader("Unregistered Strategies"),
            html.Div([strategy_card(s, registered=False) for s in unregistered]),
        ]
    )


@callback(
    Output("strategy-register-output", "children"),
    Output("refresh-strategies", "data"),
    Input({"type": "register-btn", "index": dash.ALL}, "n_clicks"),
    Input({"type": "unregister-btn", "index": dash.ALL}, "n_clicks"),
    State({"type": "register-btn", "index": dash.ALL}, "id"),
    State({"type": "unregister-btn", "index": dash.ALL}, "id"),
    prevent_initial_call=True,
)
def toggle_strategy(register_clicks, unregister_clicks, register_ids, unregister_ids):
    triggered = ctx.triggered_id
    new_data = str(uuid.uuid4())

    if not triggered:
        return dbc.Alert("No action taken.", color="warning", dismissable=True), new_data

    if triggered["type"] == "register-btn":
        index = next((i for i, id_ in enumerate(register_ids) if id_["index"] == triggered["index"]), None)
        clicks = register_clicks[index] if index is not None and register_clicks[index] is not None else 0
        if clicks <= 0:
            return dash.no_update, dash.no_update

        strategy_id = triggered["index"]
        CoreLogger().info(f"Registering strategy {strategy_id}")
        all_discovered = discover_strategies(STRATEGY_FOLDER)
        match = next((s for s in all_discovered if s["id"] == strategy_id), None)
        if match:
            try:
                register_strategy(match)
                return dbc.Alert(f"✅ Registered strategy {strategy_id}", color="success", dismissable=True), new_data
            except Exception as e:
                return dbc.Alert(f"Error during registration: {e}", color="danger", dismissable=True), new_data
        return dbc.Alert(f"⚠️ Strategy {strategy_id} not found.", color="danger", dismissable=True), new_data

    elif triggered["type"] == "unregister-btn":
        index = next((i for i, id_ in enumerate(unregister_ids) if id_["index"] == triggered["index"]), None)
        clicks = unregister_clicks[index] if index is not None and unregister_clicks[index] is not None else 0
        if clicks <= 0:
            return dash.no_update, dash.no_update

        strategy_id = triggered["index"]
        CoreLogger().info(f"Unregistering strategy {strategy_id}")
        try:
            unregister_strategy(strategy_id)
            return dbc.Alert(f"🗑️ Unregistered strategy {strategy_id}", color="secondary", dismissable=True), new_data
        except Exception as e:
            return dbc.Alert(f"Error during unregister: {e}", color="danger", dismissable=True), new_data

    return dbc.Alert("Unhandled action.", color="warning", dismissable=True), new_data
