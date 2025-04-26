from dash import html, dcc
import dash_bootstrap_components as dbc


def LogViewer():
    return html.Div(
        [
            # Tiny always-visible footer
            html.Div(
                [
                    html.Div(id="log-preview", style={"fontSize": "12px", "cursor": "pointer"}),
                    dcc.Interval(id="log-refresh", interval=3000, n_intervals=0),
                ],
                id="log-preview-container",
                style={"position": "fixed", "top": 0, "width": "100%", "backgroundColor": "#f8f9fa", "zIndex": 999},
            ),
            dbc.Modal(
                [
                    dbc.ModalHeader(dbc.ModalTitle("Application Logs")),
                    dbc.ModalBody(html.Pre(id="full-log-output", style={"maxHeight": "500px", "overflowY": "scroll"})),
                ],
                id="log-modal",
                is_open=False,
                size="xl",
                scrollable=True,
            ),
        ]
    )
