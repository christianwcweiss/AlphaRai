from typing import Optional

from components.atoms.atom import Atom
from constants import colors
from dash import html
from dash.development.base_component import Component
from exceptions.ui import ComponentPropertyError


class SectionHeader(Atom):  # pylint: disable=too-few-public-methods
    """Section header component for Dash applications."""

    DEFAULT_STYLE = {"marginBottom": "0.25rem", "marginTop": "20px", "color": colors.PRIMARY_COLOR}

    def __init__(self, title: str, subtitle: Optional[str] = None) -> None:
        self._title = title
        self._subtitle = subtitle

    def validate(self) -> None:
        if self._title == "":
            raise ComponentPropertyError(
                "Title cannot be empty. Please provide a valid title for the SectionHeader component."
            )

    def render(self) -> Component:
        return html.Div(
            children=[
                html.H2(self._title, style=self.DEFAULT_STYLE),
                (
                    html.P(self._subtitle, style={"marginTop": "0", "color": colors.TEXT_PRIMARY, "fontSize": "1rem"})
                    if self._subtitle
                    else None
                ),
            ],
            style={
                "paddingBottom": "1.5rem",
                "marginBottom": "1rem",
            },
        )
