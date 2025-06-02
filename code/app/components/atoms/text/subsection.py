from typing import Any, Dict, Optional

from components.atoms.atom import Atom
from constants import colors
from dash import html
from exceptions.ui import ComponentPropertyError


class SubsectionHeader(Atom):
    """A subsection header component for Dash applications."""

    DEFAULT_STYLE = {
        "paddingTop": "1rem",
        "marginTop": "1rem",
    }

    TITLE_STYLE = {
        "marginTop": "0.5rem",
        "color": colors.SECONDARY_COLOR,
        "fontSize": "1.25rem",
    }

    def __init__(
        self,
        title: str,
        style: Optional[Dict[str, Any]] = None,
    ):
        self._title = title
        self._style = {**self.DEFAULT_STYLE, **(style or {})}

        self.validate()

    def validate(self) -> None:
        if not self._title:
            raise ComponentPropertyError("Subsection title cannot be empty. Please provide a valid title.")

    def render(self) -> html.Div:
        return html.Div(
            children=[html.H3(self._title, style=self.TITLE_STYLE)],
            style=self._style,
        )
