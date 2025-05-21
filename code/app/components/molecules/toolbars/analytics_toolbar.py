import dash_bootstrap_components as dbc
from dash import html, dcc
from dash.development.base_component import Component

from components.molecules.molecule import Molecule

FILTERS = [
    ("Account ID", "filter-by-account_id"),
    ("Symbol", "filter-by-symbol"),
    ("Asset Type", "filter-by-asset-type"),
]
GROUPS = [
    ("Account ID", "group-by-account_id"),
    ("Symbol", "group-by-symbol"),
    ("Asset Type", "group-by-asset-type"),
    ("Hour of Day", "group-by-hour"),
    ("Day of Week", "group-by-weekday"),
]


class AnalyticsToolbarMolecule(Molecule):
    STYLE = {"marginBottom": "20px"}

    def render(self) -> Component:
        return html.Div(
            [
                html.Div(
                    [
                        html.Div(
                            [
                                html.Label(label, htmlFor=dropdown_id, style={"marginRight": "8px"}),
                                dcc.Dropdown(
                                    id=dropdown_id,
                                    options=[],  # To be filled via callback
                                    multi=True,
                                    placeholder=f"Select {label}",
                                    style={"minWidth": "200px", "marginRight": "16px"},
                                ),
                            ],
                            style={"display": "inline-block", "verticalAlign": "top"},
                        )
                        for label, dropdown_id in FILTERS
                    ],
                    style={"display": "flex", "flexWrap": "wrap", "alignItems": "center", "gap": "16px"},
                ),
                html.Br(),
                html.Div(
                    [
                        html.Span("Group by: ", style={"marginRight": "10px", "fontWeight": "bold"}),
                        dbc.ButtonGroup(
                            [
                                dbc.Button(
                                    label,
                                    id=button_id,
                                    color="secondary",
                                    outline=True,
                                    active=False,
                                    n_clicks=0,
                                )
                                for label, button_id in GROUPS
                            ],
                            size="sm",
                        ),
                    ],
                    style={"marginTop": "10px"},
                ),
            ],
            style=self.STYLE,
        )
