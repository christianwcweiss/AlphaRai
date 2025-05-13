import string
from typing import Optional, Dict, Any, Union, List

from dash import html
from dash.development.base_component import Component

from components.atoms.atom import Atom
from constants import colors
from exceptions.ui import ComponentPropertyError


class AlphaToolbarButton(Atom):
    """A button component for Dash, allowing for various styles and states."""

    DEFAULT_STYLE = {
        "backgroundColor": colors.LIGHT_GREY,
        "color": colors.DARK_TEXT_COLOR,
        "padding": "0.5rem 1rem",
        "border": f"1px solid {colors.GREY_BORDER}",
        "borderRadius": "0.4rem",
        "textAlign": "center",
        "cursor": "pointer",
        "fontWeight": "500",
        "fontSize": "0.9rem",
        "transition": "background-color 0.2s ease",
        "userSelect": "none",
        "display": "inline-block",
        "margin": "0 5px",
    }

    def __init__(
        self,
        label: str,
        button_id: Optional[Union[str, Dict[str, Any]]] = None,
        style: Optional[Dict[str, Any]] = None,
    ):
        self._label = label
        self._id = (
            button_id
            if button_id
            else f"toolbar-button-{''.join([c for c in label if c in string.ascii_letters])}".lower()
        )
        self._style = {**self.DEFAULT_STYLE, **(style or {})}

        self.validate()

    def validate(self) -> None:
        if not self._label:
            raise ComponentPropertyError("ToolbarButton requires a non-empty label.")

    def render(self) -> html.Button:
        return html.Button(self._label, id=self._id, style=self._style)


class AlphaToolbar(Atom):
    """A toolbar component for Dash, allowing for a collection of buttons or controls to be displayed together."""

    DEFAULT_STYLE = {
        "display": "flex",
        "justifyContent": "center",
        "alignItems": "center",
        "gap": "10px",
        "padding": "0.75rem",
        "backgroundColor": colors.BACKGROUND_COLOR,
        "borderRadius": "0.5rem",
        "boxShadow": f"0 2px 6px {colors.SHADOW_COLOR}",
        "margin": "1rem 0",
        "flexWrap": "wrap",
    }

    def __init__(
        self,
        children: List[Component],
        toolbar_id: Optional[str] = None,
        style: Optional[Dict[str, Any]] = None,
    ):
        self._children = children
        self._id = toolbar_id or "toolbar"
        self._style = {**self.DEFAULT_STYLE, **(style or {})}

        self.validate()

    def validate(self) -> None:
        if not self._children:
            raise ComponentPropertyError("Toolbar must contain at least one ToolbarButton.")

    def render(self) -> html.Div:
        return html.Div(
            self._children,
            id=self._id,
            style=self._style,
        )
