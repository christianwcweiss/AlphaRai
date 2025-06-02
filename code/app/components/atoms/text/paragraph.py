from typing import Any, Dict, Optional

from components.atoms.atom import Atom
from constants import colors
from dash import html
from exceptions.ui import ComponentPropertyError


class Paragraph(Atom):
    """A paragraph component for Dash applications."""

    DEFAULT_STYLE = {
        "marginTop": "0.25rem",
        "marginBottom": "0.75rem",
        "color": colors.TEXT_ON_ACCENT,
        "fontSize": "0.95rem",
        "lineHeight": "1.5",
    }

    def __init__(
        self,
        text: str,
        style: Optional[Dict[str, Any]] = None,
    ):
        self._text = text
        self._style = {**self.DEFAULT_STYLE, **(style or {})}

        self.validate()

    def validate(self) -> None:
        if not self._text:
            raise ComponentPropertyError("Paragraph text cannot be empty. Please provide valid content.")

    def render(self) -> html.P:
        return html.P(
            children=self._text,
            style=self._style,
        )
