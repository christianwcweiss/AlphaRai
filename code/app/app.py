import argparse
import os
from argparse import Namespace

import dash
import dash_bootstrap_components as dbc
from components.atoms.buttons.general.floating_action_button import AlphaFloatingActionButton
from components.frame.top_bar import TopBar
from components.molecules.banners.bot_status.banner import BotStatusBanner
from components.molecules.modals.logs.log_viewer import LogViewer
from components.molecules.modals.trades.new_trade import NewTradeModal
from constants import colors
from dash import ALL, Dash, Input, Output, State, callback_context, dcc, html, no_update, page_container
from db.database import init_db
from quant_core.services.core_logger import CoreLogger
from services.relay_bot import DiscordRelayBot


def parse_args() -> Namespace:
    parser = argparse.ArgumentParser(description="Run the Dash application.")
    parser.add_argument("--debug", action="store_true", help="Run the app in debug mode with hot-reloading.")
    return parser.parse_args()


def create_app() -> Dash:
    init_db()

    app = Dash(__name__, use_pages=True, external_stylesheets=[dbc.themes.COSMO])
    app.config.suppress_callback_exceptions = False  # Optional, safe to leave False

    trade_store_id = "parsed-trade-store"

    app.layout = dbc.Container(
        [
            dcc.Interval(id="topbar-bot-status-interval", interval=2000, n_intervals=0),
            dcc.Location(id="url", refresh=False),
            dcc.Store(id="topbar-account-store", data={"refresh": True}),
            html.Div(id="dummy-toggle-response", style={"display": "none"}),
            TopBar(bot_status_component=BotStatusBanner(is_running=False).render()),
            LogViewer().render(),
            page_container,
            NewTradeModal().render(),
            dcc.Store(id=trade_store_id),
            html.Div(id="trade-status"),
            AlphaFloatingActionButton("+", "open-trade-modal-btn").render(),
        ],
        fluid=True,
        style={"backgroundColor": colors.GREY_100, "minHeight": "100vh"},
    )

    register_callbacks(app)
    return app


def register_callbacks(app: Dash):
    @app.callback(Output("log-preview", "children"), Input("log-refresh", "n_intervals"))
    def update_log_preview(_):
        try:
            with open(CoreLogger().log_file_path, "r", encoding="utf-8") as f:
                lines = f.readlines()
            return " • ".join(line.strip() for line in lines[-1:])
        except Exception as error:
            return f"Log preview error: {error}"

    @app.callback(
        Output("log-modal", "is_open"),
        Output("full-log-output", "children"),
        Input("log-preview", "n_clicks"),
        State("log-modal", "is_open"),
        prevent_initial_call=True,
    )
    def toggle_log_modal(_, is_open: bool):
        if not is_open:
            try:
                with open(CoreLogger().log_file_path, "r", encoding="utf-8") as f:
                    full_logs = f.read()
            except Exception as error:
                full_logs = f"Error loading logs: {error}"
            return True, full_logs
        return False, no_update

    @app.callback(
        Output("topbar-bot-status", "children"),
        Input("topbar-bot-status-interval", "n_intervals"),
        Input("topbar-toggle-bot-button", "n_clicks"),
    )
    def update_bot_status(_, __):
        ctx = callback_context
        triggered_id = ctx.triggered_id

        bot = DiscordRelayBot()

        if triggered_id == "topbar-toggle-bot-button":
            if bot.is_running():
                CoreLogger().info("TopBar button pressed: stopping bot.")
                bot.stop()
            else:
                CoreLogger().info("TopBar button pressed: starting bot.")
                bot.run()

        status = bot.is_running()

        return BotStatusBanner(is_running=status).render()

    @app.callback(
        Output("topbar-enabled-accounts", "children"),
        Output("topbar-account-dropdown", "children"),
        Input("topbar-account-store", "data"),
    )
    def populate_account_dropdown(_data):
        from services.db.main.account import AccountService

        accounts = AccountService().get_all_accounts()
        enabled_count = sum(a.enabled for a in accounts)

        dropdown_items = [
            dbc.DropdownMenuItem(
                f"{a.friendly_name} {'✅' if a.enabled else '❌'}",
                id={"type": "account-toggle", "index": a.uid},
            )
            for a in accounts
        ]

        return f"Enabled Accounts: {enabled_count}", dropdown_items

    @app.callback(
        Output("dummy-toggle-response", "children"),
        Input({"type": "account-toggle", "index": ALL}, "n_clicks"),
        prevent_initial_call=True,
    )
    def toggle_account(_toggle_clicks: int) -> str:
        from services.db.main.account import AccountService

        ctx = callback_context
        if not ctx.triggered_id:
            return no_update

        if ctx.triggered[0]["value"] in (None, 0):
            return no_update

        account_uid = ctx.triggered_id["index"]
        svc = AccountService()
        account = svc.get_account_by_uid(account_uid)
        account.enabled = not account.enabled
        svc.toggle_account_enabled(account.uid)

        return f"Toggled account {account_uid}"


if __name__ == "__main__":
    if os.environ.get("WERKZEUG_RUN_MAIN") == "true":
        bot_instance = DiscordRelayBot()
        bot_instance.run()

    args = parse_args()
    app = create_app()
    app.run(debug=args.debug)
