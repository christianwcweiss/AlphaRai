import base64
import os
from typing import Optional

from dash import html, dcc
import dash_bootstrap_components as dbc
import plotly.graph_objs as go
from components.atoms.card.card import AlphaCard, AlphaCardHeader, AlphaCardBody
from components.charts.chart import ChartLayoutStyle, ChartMargin
from components.charts.line.line_chart import LineChart
from models.main.account import Account
import pandas as pd


class AccountSettingsCard:  # pylint: disable=too-few-public-methods
    """A card that displays account settings and a chart."""

    def __init__(
        self, account: Account, enabled_count: int, total_count: int, data_frame: Optional[pd.DataFrame] = None
    ):
        self.account = account
        self.enabled_count = enabled_count
        self.total_count = total_count
        self.data_frame = data_frame
        self.icon_id = f"account-options-btn-{account.id}"
        self.popover_id = f"account-options-popover-{account.id}"
        self.delete_btn_id = f"delete-account-{account.uid}"

    def _encode_image(self, file_path: str) -> str:
        """Encodes an image to base64."""
        with open(file_path, "rb") as f:
            return base64.b64encode(f.read()).decode()

    def _render_header(self) -> html.Div:
        icon_path = os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", "assets")
        mt5_icon = self._encode_image(os.path.join(icon_path, "images", "mt5_logo.png"))
        more_icon = self._encode_image(os.path.join(icon_path, "icons", "more_vertical.png"))
        delete_icon = self._encode_image(os.path.join(icon_path, "icons", "delete.png"))

        return AlphaCardHeader(
            html.Div(
                [
                    html.A(
                        html.Div(
                            [
                                html.Img(
                                    src=f"data:image/png;base64,{mt5_icon}",
                                    style={"height": "24px", "marginRight": "0.5rem"},
                                ),
                                html.H5(self.account.friendly_name or self.account.uid, style={"margin": 0}),
                            ],
                            style={"display": "flex", "alignItems": "center"},
                        ),
                        href=f"/settings/accounts/{self.account.uid}",
                        style={"textDecoration": "none", "color": "inherit"},
                    ),
                    html.Img(
                        id=self.icon_id,
                        src=f"data:image/png;base64,{more_icon}",
                        style={"width": "20px", "height": "20px", "cursor": "pointer"},
                        n_clicks=0,
                    ),
                    dbc.Popover(
                        dbc.PopoverBody(
                            html.Div(
                                [
                                    html.Img(
                                        src=f"data:image/png;base64,{delete_icon}",
                                        style={"width": "20px", "marginRight": "0.5rem"},
                                    ),
                                    html.Span("Delete"),
                                ],
                                id={"type": "delete", "index": self.account.uid},
                                n_clicks=0,
                                style={"display": "flex", "alignItems": "center", "cursor": "pointer"},
                            )
                        ),
                        id=self.popover_id,
                        target=self.icon_id,
                        placement="bottom-end",
                        trigger="legacy",
                        is_open=False,
                    ),
                ],
                style={
                    "display": "flex",
                    "justifyContent": "space-between",
                    "alignItems": "center",
                    "width": "100%",
                },
            )
        ).render()

    def _render_body(self) -> html.Div:
        # Chart
        if self.data_frame is not None and not self.data_frame.empty:
            line_chart_layout_style = ChartLayoutStyle(
                title="",
                x_axis_title="",
                y_axis_title="",
                margin=ChartMargin(
                    left=0,
                    right=0,
                    top=0,
                    bottom=0,
                ),
                show_legend=False,
                show_title=False,
                show_x_title=False,
                show_y_title=False,
                show_x_grid=False,
                show_y_grid=False,
                show_x_axis=False,
                show_y_axis=False,
            )
            fig = LineChart(
                data_frame=self.data_frame,
                line_layout_style=line_chart_layout_style,
            ).plot(
                x_col="closed_at",
                y_col="relative_balance",
            )
        else:
            fig = go.Figure(layout=go.Layout(title="No Data", height=100))

        return AlphaCardBody(
            [
                dcc.Graph(
                    figure=fig,
                    config={"displayModeBar": False},
                    style={"height": "100px"},
                ),
            ]
        ).render()

    def render(self) -> html.Div:
        """Renders the account settings card."""
        return AlphaCard(
            header=self._render_header(),
            body=self._render_body(),
            style={"backgroundColor": "#ffffff"},
        ).render()
