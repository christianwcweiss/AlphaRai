import string
from typing import Any, Dict, List, Optional

import dash_bootstrap_components as dbc
from components.atoms.atom import Atom
from constants import colors
from dash import html
from exceptions.ui import ComponentPropertyError


class AlphaButtonGroup(Atom):
    """A button group component for Dash, allowing for multiple buttons with various styles and states."""

    DEFAULT_BUTTON_STYLE = {
        "backgroundColor": "transparent",
        "color": colors.PRIMARY_COLOR,
        "fontWeight": "600",
        "fontSize": "0.9rem",
        "borderRadius": "0.5rem",
        "border": f"2px solid {colors.PRIMARY_COLOR}",
    }

    ACTIVE_BUTTON_STYLE = {
        "backgroundColor": colors.PRIMARY_COLOR,
        "color": colors.TEXT_SECONDARY,
        "fontWeight": "600",
        "fontSize": "0.9rem",
        "borderRadius": "0.5rem",
        "border": f"2px solid {colors.PRIMARY_COLOR}",
    }

    def __init__(
        self,
        buttons: List[Dict[str, Any]],
        group_id: Optional[str] = None,
        size: Optional[str] = "sm",
        radio_toggle: bool = False,  # keep it false unless verified version 3+
    ) -> None:
        """
        buttons: List of dicts with keys: label, id (optional), active (optional), style (optional)
        """
        self._buttons = buttons
        self._group_id = group_id or "button-group"
        self._size = size
        self._radio_toggle = radio_toggle

        self.validate()

    def validate(self) -> None:
        if not self._buttons or not isinstance(self._buttons, list):
            raise ComponentPropertyError("You must provide a non-empty list of button definitions.")

    def _generate_buttons(self) -> List[dbc.Button]:
        buttons = []

        for btn in self._buttons:
            is_active = btn.get("active", False)
            style = {**(self.ACTIVE_BUTTON_STYLE if is_active else self.DEFAULT_BUTTON_STYLE)}
            style.update(btn.get("style", {}))  # Allow user overrides

            buttons.append(
                dbc.Button(
                    btn["label"],
                    id=btn.get("id", self._generate_id(btn["label"])),
                    active=is_active,  # ✅ Let Dash update this dynamically
                    color="primary",
                    outline=True,
                    style=style,
                    n_clicks=btn.get("n_clicks", 0),
                )
            )

        return buttons

    def _generate_id(self, label: str) -> str:
        safe = "".join([c for c in label if c in string.ascii_letters])
        return f"{self._group_id}-{safe.lower()}"

    def render(self) -> html.Div:
        group_props = {
            "children": self._generate_buttons(),
            "size": self._size,
            "id": self._group_id,
        }

        # Only pass `type` if you're sure it's supported (manually set radio_toggle=True in code)
        if self._radio_toggle:
            group_props["type"] = "radio"

        return html.Div(dbc.ButtonGroup(**group_props))
