from typing import Optional

from dash import html
from dash.development.base_component import Component

from components.atoms.atom import Atom
from constants import colors


class SectionHeader(Atom):
    def __init__(self, title: str, subtitle: Optional[str] = None) -> None:
        self._title = title
        self._subtitle = subtitle

    def render(self) -> Component:
        return html.Div(
            children=[
                html.H2(self._title, style={"marginBottom": "0.25rem", "color": colors.PRIMARY_COLOR}),
                (
                    html.P(self._subtitle, style={"marginTop": "0", "color": colors.TEXT_COLOR, "fontSize": "1rem"})
                    if self._subtitle
                    else None
                ),
            ],
            style={
                "paddingBottom": "1.5rem",
                "marginBottom": "1rem",
            },
        )
