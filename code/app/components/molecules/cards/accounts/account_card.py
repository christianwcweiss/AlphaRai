import os
from typing import Optional

import dash_bootstrap_components as dbc
import pandas as pd
from components.atoms.card.card import AlphaCard, AlphaCardBody, AlphaCardHeader
from components.charts.chart import ChartLayoutStyle, ChartMargin
from components.charts.line.line_chart import LineChart
from constants import colors
from dash import dcc, html
from models.main.account import Account
from quant_core.enums.prop_firm import PropFirm
from quant_core.utils.image_utils import encode_image


class AccountCard:  # pylint: disable=too-few-public-methods
    """A card that displays account settings and a chart."""

    def __init__(self, account: Account, data_frame: Optional[pd.DataFrame] = None) -> None:
        self._account = account
        self._data_frame = data_frame
        self._icon_id = f"account-options-btn-{account.id}"
        self._popover_id = f"account-options-popover-{account.id}"
        self._delete_btn_id = f"delete-account-{account.uid}"

    def _render_header(self) -> html.Div:
        icon_path = os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", "..", "assets", "icons", "general")
        more_icon = encode_image(os.path.join(icon_path, "more_vertical.png"))
        delete_icon = encode_image(os.path.join(icon_path, "delete.png"))

        company_logo_path = PropFirm(self._account.prop_firm).get_company_logo()
        company_logo = encode_image(company_logo_path)

        return AlphaCardHeader(
            html.Div(
                [
                    html.A(
                        html.Div(
                            [
                                html.Img(
                                    src=f"data:image/png;base64,{company_logo}",
                                    style={"height": "24px", "marginRight": "0.5rem"},
                                ),
                                html.H5(self._account.friendly_name or self._account.uid, style={"margin": 0}),
                            ],
                            style={"display": "flex", "alignItems": "center"},
                        ),
                        href=f"/accounts/{self._account.uid}",
                        style={"textDecoration": "none", "color": "inherit"},
                    ),
                    html.Img(
                        id=self._icon_id,
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
                                id={"type": "initiate-delete", "index": self._account.uid},
                                n_clicks=0,
                                style={"display": "flex", "alignItems": "center", "cursor": "pointer"},
                            )
                        ),
                        id=self._popover_id,
                        target=self._icon_id,
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

    def _render_balance_preview(self) -> html.Div:
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
            data_frame=self._data_frame,
            line_layout_style=line_chart_layout_style,
        ).plot(
            x_col="closed_at",
            y_col="relative_balance",
        )

        return AlphaCardBody(
            [
                dcc.Graph(
                    figure=fig,
                    config={"displayModeBar": False},
                    style={"height": "100px"},
                ),
            ]
        ).render()

    def _render_no_data_available(self) -> html.Div:
        return html.Div(
            "No data available for this account.",
            style={"height": "100px", "textAlign": "center", "color": colors.PRIMARY_COLOR},
        )

    def _render_body(self) -> html.Div:
        # Chart
        if self._data_frame is not None and not self._data_frame.empty:
            return self._render_balance_preview()

        return self._render_no_data_available()

    def render(self) -> html.Div:
        """Renders the account settings card."""
        return AlphaCard(
            header=self._render_header(),
            body=self._render_body(),
            style={"backgroundColor": "#ffffff"},
        ).render()
