import argparse
import os
from argparse import Namespace

import dash_bootstrap_components as dbc
from components.atoms.buttons.general.floating_action_button import AlphaFloatingActionButton
from components.frame.top_bar import TopBar
from components.molecules.modals.logs.log_viewer import LogViewer
from components.molecules.modals.trades.new_trade import NewTradeModal
from constants import colors
from dash import Dash, Input, Output, State, callback, dash, dcc, html, page_container
from db.database import init_db
from quant_core.services.core_logger import CoreLogger
from services.relay_bot import DiscordRelayBot  # pylint: disable=unused-import  # noqa: F401


def parse_args() -> Namespace:
    """Parse command line arguments."""

    parser = argparse.ArgumentParser(description="Run the Dash application.")

    parser.add_argument(
        "--debug",
        action="store_true",
        help="Run the app in debug mode with hot-reloading.",
    )

    return parser.parse_args()


def main() -> Dash:
    """Initialize the Dash application and set up the layout."""
    init_db()

    dash_app = Dash(__name__, use_pages=True, external_stylesheets=[dbc.themes.COSMO])

    trade_store_id = "parsed-trade-store"
    dash_app.layout = dbc.Container(
        [
            dcc.Location(id="url", refresh=False),
            TopBar(),
            LogViewer().render(),
            page_container,
            NewTradeModal().render(),
            dcc.Store(id=trade_store_id),
            html.Div(id="trade-status"),
            AlphaFloatingActionButton(
                "+",
                "open-trade-modal-btn",
            ).render(),
        ],
        fluid=True,
        style={"backgroundColor": colors.GREY_100, "minHeight": "100vh"},
    )

    return dash_app


@callback(Output("log-preview", "children"), Input("log-refresh", "n_intervals"))
def update_log_preview(_) -> str:
    """Update the log preview with the latest log entry."""
    try:
        with open(CoreLogger().log_file_path, "r", encoding="utf-8") as f:
            lines = f.readlines()
        return " • ".join(line.strip() for line in lines[-1:])
    except Exception as error:  # pylint: disable=broad-exception-caught
        return f"Log preview error: {error}"


@callback(
    Output("log-modal", "is_open"),
    Output("full-log-output", "children"),
    Input("log-preview", "n_clicks"),
    State("log-modal", "is_open"),
    prevent_initial_call=True,
)
def toggle_log_modal(_, is_open: bool) -> tuple[bool, str]:
    """Toggle the log modal and display the full logs."""
    if not is_open:
        try:
            with open(CoreLogger().log_file_path, "r", encoding="utf-8") as f:
                full_logs = f.read()
        except Exception as error:  # pylint: disable=broad-exception-caught
            full_logs = f"Error loading logs: {error}"
        return True, full_logs
    return False, dash.no_update


if __name__ == "__main__":
    if os.environ.get("WERKZEUG_RUN_MAIN") == "true":  # Avoid starting the bot multiple times in debug mode
        bot_instance = DiscordRelayBot()
        bot_instance.run()

    arguments = parse_args()
    debug_mode = arguments.debug

    app = main()
    app.run(debug=debug_mode)
