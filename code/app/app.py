from dash import dcc, page_container, Dash, callback, Output, Input, State, dash, html
import dash_bootstrap_components as dbc

from components.atoms.buttons.button import AlphaButton
from components.molecules.modals.logs.log_viewer import LogViewer
from components.frame.top_bar import TopBar
from components.molecules.modals.trades.new_trade import NewTradeModal
from constants import colors
from db.database import init_db
from quant_core.services.core_logger import CoreLogger


init_db()
app = Dash(__name__, use_pages=True, external_stylesheets=[dbc.themes.COSMO], suppress_callback_exceptions=True)
server = app.server

TRADE_STORE_ID = "parsed-trade-store"


app.layout = dbc.Container([
    dcc.Location(id="url", refresh=False),
    TopBar(),
    LogViewer().render(),
    page_container,
    NewTradeModal().render(),
    dcc.Store(id=TRADE_STORE_ID),
    html.Div(id="trade-status"),
    AlphaButton(
        "+",
        "open-trade-modal-btn",
        style={
            "position": "fixed",
            "bottom": "30px",
            "right": "30px",
            "zIndex": 1050,
            "borderRadius": "50%",
            "width": "60px",
            "height": "60px",
            "padding": "0",
            "fontSize": "28px",
            "boxShadow": "0 4px 12px rgba(0,0,0,0.2)",
            "backgroundColor": colors.PRIMARY_COLOR,
            "color": "#fff",
        }
    ).render()
], fluid=True)


@callback(Output("log-preview", "children"), Input("log-refresh", "n_intervals"))
def update_log_preview(_):
    try:
        with open(CoreLogger().log_file_path, "r", encoding="utf-8") as f:
            lines = f.readlines()
        return " • ".join(line.strip() for line in lines[-1:])
    except Exception as e:
        return f"Log preview error: {e}"


@callback(
    Output("log-modal", "is_open"),
    Output("full-log-output", "children"),
    Input("log-preview", "n_clicks"),
    State("log-modal", "is_open"),
    prevent_initial_call=True,
)
def toggle_log_modal(_, is_open):
    if not is_open:
        try:
            with open(CoreLogger().log_file_path, "r", encoding="utf-8") as f:
                full_logs = f.read()
        except Exception as e:
            full_logs = f"Error loading logs: {e}"
        return True, full_logs
    return False, dash.no_update


if __name__ == "__main__":
    app.run(debug=True)
