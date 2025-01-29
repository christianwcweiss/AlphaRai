
from dash import dcc, page_container, Dash, callback, Output, Input, State, ctx, dash
import dash_bootstrap_components as dbc

from components.atoms.logs.log_viewer import LogViewer
from components.frame.top_bar import TopBar
from db.database import init_db
from quant_core.services.core_logger import CoreLogger


init_db()
app = Dash(__name__, use_pages=True, external_stylesheets=[dbc.themes.COSMO])
server = app.server


app.layout = dbc.Container([
    dcc.Location(id="url", refresh=False),
    TopBar(),
    LogViewer(),
    page_container
], fluid=True)


@callback(
    Output("log-preview", "children"),
    Input("log-refresh", "n_intervals")
)
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
    prevent_initial_call=True
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

if __name__ == '__main__':
    app.run(debug=True)
