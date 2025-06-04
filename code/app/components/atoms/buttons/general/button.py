import string
from enum import Enum
from typing import Any, Dict, Optional, Union

from components.atoms.atom import Atom
from constants import colors
from dash import html
from exceptions.ui import ComponentPropertyError


class AlphaButtonVariant(Enum):
    """Enumeration for button variants."""

    CONTAINED = "contained"


class AlphaButtonIcon(Enum):
    """Enumeration for button icons."""

    ADD = "add"
    DELETE = "delete"
    EDIT = "edit"
    SAVE = "save"
    CANCEL = "cancel"
    REFRESH = "refresh"
    SETTINGS = "settings"
    SEARCH = "search"


class AlphaButtonColor(Enum):
    """Enumeration for button colors."""

    PRIMARY = colors.PRIMARY_COLOR
    SECONDARY = colors.SECONDARY_COLOR
    SUCCESS = colors.SUCCESS_COLOR
    ERROR = colors.ERROR_COLOR
    WARNING = colors.WARNING_COLOR
    CONFIRM = colors.SUCCESS_COLOR
    CANCEL = colors.ERROR_COLOR


class AlphaButton(Atom):
    """A button component for Dash applications."""

    def __init__(
        self,
        label: str,
        button_id: Optional[Union[str, Dict[str, Any]]] = None,
        href: Optional[str] = None,
        width: str = "100%",
        height: str = "50px",
        button_variant: AlphaButtonVariant = AlphaButtonVariant.CONTAINED,
        button_color: AlphaButtonColor = AlphaButtonColor.PRIMARY,
        start_icon: Optional[AlphaButtonIcon] = None,
        end_icon: Optional[AlphaButtonIcon] = None,
        hidden: bool = False,
    ) -> None:
        self._label = label
        self._id = (
            button_id if button_id else f"button-{''.join([c for c in label if c in string.ascii_letters])}".lower()
        )
        self._href = href
        self._width = width
        self._height = height
        self._button_variant = button_variant
        self._button_color = button_color
        self._start_icon = start_icon
        self._end_icon = end_icon
        self._hidden = hidden

        self.validate()

    def validate(self) -> None:
        if self._label == "":
            raise ComponentPropertyError("Label cannot be empty. Please provide a valid label for the button.")

    def _build_style(self) -> Dict[str, Any]:
        return {
            "backgroundColor": self._button_color.value,
            "color": colors.get_text_color(self._button_color.value),
            "fontWeight": "bold",
            "width": self._width,
            "border": "none",
            "padding": "10px",
            "borderRadius": "5px",
            "height": self._height,
            "boxShadow": f"0px 2px 6px {colors.SHADOW_COLOR}",
        }

    def render(self) -> html.Div:
        """Render the button as a Dash HTML component."""

        button = html.Button(self._label, id=self._id, style=self._build_style())

        if self._href:
            button = html.A(
                button,
                href=self._href,
                style={"textDecoration": "none", "color": "inherit", "display": "inline-block"},
            )

        return html.Div(
            children=[button],
            style={
                "display": "inline-block",
                "visibility": "hidden" if self._hidden else "visible",
                "width": self._width,
                "height": self._height,
            },
        )
