import dash_bootstrap_components as dbc
from components.molecules.molecule import Molecule
from constants import colors
from dash import dcc, html

_LOG_VIEWER_STYLE = {
    "position": "fixed",
    "top": 0,
    "width": "100%",
    "backgroundColor": colors.BACKGROUND_COLOR,
    "zIndex": 999,
}
_LOG_MODAL_STYLE = {
    "maxHeight": "50rem",
    "overflowY": "scroll",
    "backgroundColor": colors.BACKGROUND_COLOR,
}


class LogViewer(Molecule):  # pylint: disable=too-few-public-methods
    """Log viewer component."""

    def render(self) -> html.Div:
        return html.Div(
            [
                html.Div(
                    [
                        html.Div(id="log-preview", style={"fontSize": "12px", "cursor": "pointer"}),
                        dcc.Interval(id="log-refresh", interval=3000, n_intervals=0),
                    ],
                    id="log-preview-container",
                    style=_LOG_VIEWER_STYLE,
                ),
                dbc.Modal(
                    [
                        dbc.ModalHeader(dbc.ModalTitle("Application Logs")),
                        dbc.ModalBody(html.Pre(id="full-log-output", style=_LOG_MODAL_STYLE)),
                    ],
                    id="log-modal",
                    is_open=False,
                    size="xl",
                    scrollable=True,
                ),
            ]
        )
