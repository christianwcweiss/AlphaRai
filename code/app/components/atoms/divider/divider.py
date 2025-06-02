from typing import Optional, Dict, Any

from dash import html

from components.atoms.atom import Atom
from constants import colors


class Divider(Atom):
    """A simple, horizontal divider line for Dash apps."""

    DEFAULT_STYLE: Dict[str, Any] = {
        "height": "1px",
        "width": "100%",
        "backgroundColor": colors.GREY_300,
        "margin": "16px 0",
        "border": "none",
        "padding": "0",
    }

    def __init__(  # pylint: disable=too-many-arguments, too-many-positional-arguments
        self,
        style: Optional[Dict[str, Any]] = None,
        thickness: Optional[str] = None,
        color: Optional[str] = None,
        margin: Optional[str] = None,
        width: Optional[str] = None,
    ):
        self._style = {**self.DEFAULT_STYLE, **(style or {})}
        if thickness:
            self._style["height"] = thickness
        if color:
            self._style["backgroundColor"] = color
        if margin:
            self._style["margin"] = margin
        if width:
            self._style["width"] = width
        self.validate()

    def validate(self) -> None:
        pass

    def render(self) -> html.Div:
        return html.Div(style=self._style)
