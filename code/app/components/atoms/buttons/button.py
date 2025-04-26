from typing import Optional, Dict, Any

from dash import html

from components.atoms.atom import Atom
from constants import colors
from exceptions.ui import ComponentPropertyError


class AlphaButton(Atom):
    DEFAULT_STYLE = {
        "backgroundColor": colors.PRIMARY_COLOR,
        "color": colors.LIGHT_TEXT_COLOR,
        "padding": "0.75rem 1.5rem",
        "border": "none",
        "borderRadius": "0.5rem",
        "textAlign": "center",
        "cursor": "pointer",
        "fontWeight": "600",
        "fontSize": "1rem",
        "transition": "background-color 0.2s ease",
        "userSelect": "none",
        "display": "inline-block",
        "width": "100%",
        "margin": "5px 0",
    }

    def __init__(
        self,
        label: str,
        button_id: Optional[str] = None,
        href: Optional[str] = None,
        style: Optional[Dict[str, Any]] = None,
    ):
        self._label = label
        self._id = button_id
        self._href = href
        self._style = {**self.DEFAULT_STYLE, **(style or {})}

        self.validate()

    def validate(self) -> None:
        if self._label == "":
            raise ComponentPropertyError(
                "Label cannot be empty. Please provide a valid label for the button."
            )


    def render(self):
        if self._href:
            return html.Div(
                html.A(
                    html.Button(self._label, id=self._id, style=self._style),
                    href=self._href,
                    style={"textDecoration": "none", "color": "inherit", "display": "inline-block"},
                )
            )
        else:
            return html.Div(html.Button(self._label, id=self._id, style=self._style))
