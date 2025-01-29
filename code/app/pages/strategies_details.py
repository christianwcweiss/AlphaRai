import dash
import dash_bootstrap_components as dbc
from dash import html, dcc, callback, Input, Output, State, MATCH, ALL
from components.atoms.content import MainContent
from components.atoms.header import PageHeader
from components.frame.body import PageBody
from pages.base_page import BasePage

from db.database import SessionLocal
from models.strategy import Strategy
from models.strategy_setting import StrategySetting
from models.credential_setting import CredentialSetting
from quant_core.services.core_logger import CoreLogger

# 🕒 Cron utilities
from quant_core.utils.time_utils import is_valid_cron, describe_cron

# ✅ Required to allow callbacks for dynamic elements
from dash.exceptions import PreventUpdate

app = dash.get_app()
app.config.suppress_callback_exceptions = True

dash.register_page(__name__, path_template="/strategies/<uid>", name="Strategy Details")


class StrategyDetailsPage(BasePage):
    def render(self):
        return PageBody([
            dcc.Location(id="strategy-details-url"),
            html.Div(id="strategy-uid", style={"display": "none"}),
            html.Div(id="dynamic-strategy-header"),
            MainContent([
                html.Div(id="strategy-details-body"),
                html.Hr(),
                html.H5("➕ Add New Setting"),
                html.Div(id="add-setting-controls"),
                html.Div(id="add-setting-result"),
                html.Hr(),
                dbc.Button("💾 Save Settings", id="save-strategy-settings", color="success", className="mt-3"),
                html.Div(id="save-settings-result", className="mt-2")
            ])
        ])


page = StrategyDetailsPage("Strategy Details")
layout = page.layout


@callback(
    Output("strategy-uid", "children"),
    Output("dynamic-strategy-header", "children"),
    Input("strategy-details-url", "pathname"),
    prevent_initial_call=True
)
def extract_uid(pathname):
    uid = pathname.split("/")[-1] if pathname else ""
    CoreLogger().info(f"🔍 Loaded Strategy Details for: {uid}")
    return uid, PageHeader(f"Strategy Details: {uid}")


@callback(
    Output("strategy-details-body", "children"),
    Output("add-setting-controls", "children"),
    Input("strategy-uid", "children"),
    prevent_initial_call=True
)
def load_strategy_details(uid):
    with SessionLocal() as session:
        strategy = session.query(Strategy).filter_by(id=uid).first()
        settings = session.query(StrategySetting).filter_by(strategy_id=uid).all()
        credentials = session.query(CredentialSetting).all()

    if not strategy:
        return dbc.Alert("⚠️ Strategy not found in the database.", color="danger", dismissable=True), dash.no_update

    credential_map = {c.uid: c.friendly_name or c.uid for c in credentials}

    strategy_card = dbc.Card([
        dbc.CardHeader("📘 Strategy Info"),
        dbc.CardBody([
            html.P(f"UID: {strategy.id}"),
            html.P(f"Friendly Name: {strategy.friendly_name or '—'}"),
            html.P(f"Type: {strategy.strategy_type}"),
            html.P(f"Hash: {strategy.strategy_hash}")
        ])
    ], className="mb-4")

    settings_list = html.Div([
        dbc.InputGroup([
            dbc.InputGroupText(credential_map.get(s.account, s.account)),
            dbc.InputGroupText(s.asset),
            dbc.Input(id={"type": "cron-input", "index": i}, value=s.cron_expression or "", placeholder="Cron expression"),
            dbc.Button("Verify", id={"type": "verify-cron", "index": i}, color="secondary", size="sm"),
            dbc.InputGroupText(id={"type": "cron-result", "index": i}),
            dbc.Checkbox(id={"type": "enable-toggle", "index": i}, value=s.enabled),
        ], className="mb-2")
        for i, s in enumerate(settings)
    ]) if settings else html.P("No settings yet for this strategy.")

    account_options = [{"label": f"{a.friendly_name or a.uid}", "value": a.uid} for a in credentials]

    add_setting_controls = dbc.InputGroup([
        dbc.Select(id="new-account", options=account_options, placeholder="Select Account"),
        dbc.Input(id="new-asset", placeholder="Asset (e.g. EURUSD)", type="text"),
        dbc.Button("Add", id="add-strategy-setting", color="primary", n_clicks=0),
    ], className="mb-3")

    return html.Div([
        strategy_card,
        html.H5("🔧 Current Settings (Account + Asset)"),
        settings_list
    ]), add_setting_controls


@callback(
    Output("add-setting-result", "children"),
    Output("strategy-details-body", "children", allow_duplicate=True),
    Input("add-strategy-setting", "n_clicks"),
    State("strategy-uid", "children"),
    State("new-account", "value"),
    State("new-asset", "value"),
    prevent_initial_call="initial_duplicate"
)
def add_strategy_setting(n_clicks, strategy_id, account, asset):
    if not account or not asset:
        raise PreventUpdate

    with SessionLocal() as session:
        strategy = session.query(Strategy).filter_by(id=strategy_id).first()
        if not strategy:
            return dbc.Alert("❌ Strategy not found!", color="danger", dismissable=True), dash.no_update

        exists = session.query(StrategySetting).filter_by(
            strategy_id=strategy_id,
            account=account,
            asset=asset
        ).first()

        if exists:
            return dbc.Alert("⚠️ This setting already exists.", color="secondary", dismissable=True), dash.no_update

        session.add(StrategySetting(
            strategy_id=strategy_id,
            strategy_hash=strategy.strategy_hash,
            account=account,
            asset=asset,
            enabled=True
        ))
        session.commit()

        CoreLogger().info(f"✅ Added setting for {strategy_id}: {account} / {asset}")
        return dbc.Alert("✅ Setting added!", color="success", dismissable=True), load_strategy_details(strategy_id)[0]


@callback(
    Output({"type": "cron-result", "index": MATCH}, "children"),
    Input({"type": "verify-cron", "index": MATCH}, "n_clicks"),
    State({"type": "cron-input", "index": MATCH}, "value"),
    prevent_initial_call=True
)
def verify_cron(_, cron):
    if is_valid_cron(cron):
        return describe_cron(cron)
    return "❌ Invalid cron"


@callback(
    Output("save-settings-result", "children"),
    Output("strategy-details-body", "children", allow_duplicate=True),
    Input("save-strategy-settings", "n_clicks"),
    State("strategy-uid", "children"),
    State({"type": "cron-input", "index": ALL}, "value"),
    State({"type": "enable-toggle", "index": ALL}, "value"),
    prevent_initial_call=True
)
def save_strategy_settings(_, strategy_id, cron_values, enabled_values):
    with SessionLocal() as session:
        settings = session.query(StrategySetting).filter_by(strategy_id=strategy_id).all()

        if len(settings) != len(cron_values):
            return dbc.Alert("❌ Internal mismatch in settings list", color="danger", dismissable=True), dash.no_update

        for s, cron, enabled in zip(settings, cron_values, enabled_values):
            s.cron_expression = cron
            s.enabled = enabled

        session.commit()
        CoreLogger().info(f"💾 Updated {len(settings)} strategy settings for {strategy_id}")
        return dbc.Alert("✅ Settings saved!", color="success", dismissable=True), load_strategy_details(strategy_id)[0]
