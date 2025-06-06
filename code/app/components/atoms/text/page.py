from typing import Any, Dict, Optional

from components.atoms.atom import Atom
from constants import colors
from dash import html
from exceptions.ui import ComponentPropertyError


class PageHeader(Atom):
    """A page header component for Dash applications, typically used to display the title and subtitle of a page."""

    DEFAULT_STYLE = {
        "paddingBottom": "1.5rem",
        "marginBottom": "1rem",
        "borderBottom": f"1px solid {colors.PRIMARY_COLOR}",
    }

    TITLE_STYLE = {
        "marginBottom": "0.25rem",
        "color": colors.PRIMARY_COLOR,
    }

    SUBTITLE_STYLE = {
        "marginTop": "0",
        "color": colors.TEXT_ON_ACCENT,
        "fontSize": "1rem",
    }

    def __init__(
        self,
        title: str,
        subtitle: Optional[str] = None,
        style: Optional[Dict[str, Any]] = None,
    ):
        self._title = title
        self._subtitle = subtitle
        self._style = {**self.DEFAULT_STYLE, **(style or {})}

        self.validate()

    def validate(self) -> None:
        if not self._title:
            raise ComponentPropertyError("Title cannot be empty. Please provide a valid title for the PageHeader.")

    def render(self) -> html.Div:
        children = [html.H1(self._title, style=self.TITLE_STYLE)]

        if self._subtitle:
            children.append(html.P(self._subtitle, style=self.SUBTITLE_STYLE))

        return html.Div(
            children=children,
            style=self._style,
        )
