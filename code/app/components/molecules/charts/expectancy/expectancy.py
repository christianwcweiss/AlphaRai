from typing import List

import pandas as pd
from components.atoms.card.card import AlphaCard, AlphaCardBody, AlphaCardHeader
from components.atoms.layout.layout import AlphaCol, AlphaRow
from components.charts.chart import ChartLayoutStyle, ChartMargin
from components.charts.line.line_chart import LineChart
from components.molecules.molecule import Molecule
from dash import dcc, html
from quant_core.enums.chart_mode import ChartMode

# IDs
EXPECTANCY_MODE_STORE_ID = "expectancy-mode-store"
EXPECTANCY_ABS_DIV_ID = "expectancy-absolute-div"
EXPECTANCY_REL_DIV_ID = "expectancy-relative-div"


class ExpectancyOverTimeMolecule(Molecule):  # pylint: disable=too-few-public-methods
    """Expectancy Over Time component."""

    def __init__(self, data_frame: pd.DataFrame) -> None:
        self._data_frame = data_frame
        self._chart_layout_style = ChartLayoutStyle(
            title="",
            x_axis_title="",
            y_axis_title="",
            show_legend=False,
            show_title=False,
            show_x_title=False,
            show_y_title=False,
            margin=ChartMargin(10, 10, 10, 10),
        )

    def _render_card_header(self) -> html.Div:
        return AlphaCardHeader(
            [
                html.Div(
                    children=[
                        html.H5("EXPECTANCY"),
                    ],
                    style={
                        "display": "flex",
                        "justifyContent": "space-between",
                        "alignItems": "center",
                        "width": "100%",
                        "paddingLeft": "10px",
                        "paddingRight": "10px",
                    },
                )
            ]
        ).render()

    def _render_absolute_chart(self, groups: List[str]) -> html.Div:
        return html.Div(
            id=EXPECTANCY_ABS_DIV_ID,
            children=[
                dcc.Graph(
                    figure=LineChart(
                        data_frame=self._data_frame,
                        line_layout_style=self._chart_layout_style,
                    ).plot(x_col="time", y_col="expectancy", group_by=groups),
                    config={"displayModeBar": True},
                )
            ],
        )

    def _render_relative_chart(self, groups: List[str]) -> html.Div:
        return html.Div(
            id=EXPECTANCY_REL_DIV_ID,
            children=[
                dcc.Graph(
                    figure=LineChart(
                        data_frame=self._data_frame,
                        line_layout_style=self._chart_layout_style,
                    ).plot(x_col="time", y_col="expectancy_pct", group_by=groups),
                    config={"displayModeBar": True},
                )
            ],
        )

    def _render_chart_body(self, groups: List[str], chart_mode: ChartMode) -> html.Div:
        return AlphaCardBody(
            children=[
                dcc.Store(id=EXPECTANCY_MODE_STORE_ID, data=ChartMode.ABSOLUTE.value),
                AlphaRow(
                    children=[
                        AlphaCol(
                            children=[
                                (
                                    self._render_absolute_chart(groups=groups)
                                    if chart_mode is ChartMode.ABSOLUTE
                                    else self._render_relative_chart(groups=groups)
                                ),
                            ]
                        )
                    ]
                ),
            ]
        ).render()

    def render(self, groups: List[str], chart_mode: ChartMode) -> html.Div:
        """Render the molecule."""
        return AlphaCard(
            header=self._render_card_header(),
            body=self._render_chart_body(groups=groups, chart_mode=chart_mode),
            style={"backgroundColor": "#FFFFFF"},
        ).render()
