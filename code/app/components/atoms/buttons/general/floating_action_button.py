from enum import Enum
from typing import Any, Dict, Optional

from components.atoms.atom import Atom
from constants import colors
from dash import html
from exceptions.ui import ComponentPropertyError


class AlphaFabSize(Enum):
    """Enumeration for Floating Action Button (FAB) sizes."""

    SMALL = "40px"
    MEDIUM = "56px"
    LARGE = "72px"


class AlphaFloatingActionButton(Atom):  # pylint: disable=too-many-instance-attributes
    """Material-style Floating Action Button (FAB)."""

    def __init__(  # pylint: disable=too-many-arguments, too-many-positional-arguments
        self,
        icon: str,  # expected as text or emoji or unicode for now
        button_id: str,
        background_color: str = colors.PRIMARY_COLOR,
        icon_color: Optional[str] = None,
        size: AlphaFabSize = AlphaFabSize.MEDIUM,
        tooltip: Optional[str] = None,
        hidden: bool = False,
        position_bottom: str = "2rem",
        position_right: str = "2rem",
    ):
        self._icon = icon
        self._id = button_id
        self._background_color = background_color
        self._icon_color = icon_color or colors.get_text_color(background_color)
        self._size = size
        self._tooltip = tooltip
        self._hidden = hidden
        self._position_bottom = position_bottom
        self._position_right = position_right

        self.validate()

    def validate(self) -> None:
        if not self._icon:
            raise ComponentPropertyError("FAB must have an icon.")

    def _build_style(self) -> Dict[str, Any]:
        return {
            "backgroundColor": self._background_color,
            "color": self._icon_color,
            "border": "none",
            "borderRadius": "50%",
            "width": self._size.value,
            "height": self._size.value,
            "boxShadow": f"0px 2px 10px {colors.SHADOW_COLOR}",
            "fontSize": "1.5rem",
            "textAlign": "center",
            "cursor": "pointer",
            "position": "fixed",
            "bottom": self._position_bottom,
            "right": self._position_right,
            "zIndex": 1000,
        }

    def render(self) -> html.Button:
        return html.Button(
            self._icon,
            id=self._id,
            title=self._tooltip or "",
            style=self._build_style(),
            hidden=self._hidden,
        )
