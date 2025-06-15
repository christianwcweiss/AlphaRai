from typing import Any, Dict

from components.molecules.molecule import Molecule
from dash import html
from dash.development.base_component import Component


class BotStatusBanner(Molecule):
    """Top bar status display with inline toggle button."""

    STYLE: Dict[str, Any] = {
        "display": "flex",
        "alignItems": "center",
        "gap": "5px",
        "fontWeight": "bold",
        "color": "white",
        "whiteSpace": "nowrap",
    }

    BUTTON_STYLE: Dict[str, Any] = {
        "background": "transparent",
        "border": "none",
        "color": "white",
        "cursor": "pointer",
        "padding": "0",
        "whiteSpace": "nowrap",
    }

    def __init__(self, is_running: bool):
        self.is_running = is_running

    def render(self, *args, **kwargs) -> Component:
        return html.Div(
            [
                html.Span("Bot:", style={"fontWeight": "normal"}),
                html.Span("Running" if self.is_running else "Stopped", style={"marginLeft": "4px"}),
                html.Button(
                    "⏹️" if self.is_running else "▶️",
                    id="topbar-toggle-bot-button",
                    title="Stop Bot" if self.is_running else "Start Bot",
                    style=self.BUTTON_STYLE | {"marginLeft": "6px"},
                ),
            ],
            id="bot-status-banner-text",
            style={
                "display": "flex",
                "alignItems": "center",
                "gap": "4px",
                "color": "white",
                "fontWeight": "bold",
                "whiteSpace": "nowrap",
            },
        )
