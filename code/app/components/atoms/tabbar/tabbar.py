from typing import List, Optional

from components.atoms.atom import Atom
from components.atoms.card.card import AlphaCard
from constants import colors
from dash import dcc, html


class AlphaTabToolbar(Atom):  # pylint: disable=too-few-public-methods
    """A toolbar for tab navigation."""

    def __init__(
        self,
        tab_labels: List[str],
        base_href: str,
        current_tab: Optional[str] = None,
        link_with_hash: bool = True,
    ):
        self.tab_labels = tab_labels
        self.base_href = base_href
        self.current_tab = current_tab or tab_labels[0]
        self.link_with_hash = link_with_hash

    def validate(self) -> None:
        if not self.tab_labels:
            raise ValueError("tab_labels cannot be empty.")
        if not isinstance(self.base_href, str):
            raise ValueError("base_href must be a string.")
        if not isinstance(self.current_tab, str):
            raise ValueError("current_tab must be a string.")
        if self.current_tab not in self.tab_labels:
            raise ValueError(f"current_tab '{self.current_tab}' is not in tab_labels.")

    def render(self) -> html.Div:
        buttons = []
        for tab in self.tab_labels:
            is_active = tab == self.current_tab
            style = {
                "backgroundColor": colors.PRIMARY_COLOR if is_active else colors.GREY_100,
                "color": colors.TEXT_ON_PRIMARY if is_active else colors.TEXT_ON_SECONDARY,
                "padding": "0.5rem 1.2rem",
                "border": "none",
                "borderRadius": "0.4rem",
                "fontWeight": "500",
                "marginRight": "10px",
                "cursor": "pointer",
                "textTransform": "capitalize",
                "transition": "background-color 0.2s ease",
            }

            buttons.append(
                dcc.Link(
                    html.Button(tab, style=style),
                    href=f"{self.base_href}#{tab}" if self.link_with_hash else f"{self.base_href}/{tab}",
                    style={"textDecoration": "none"},
                )
            )

        return html.Div(
            AlphaCard(
                children=[
                    html.Div(
                        buttons,
                        style={
                            "display": "flex",
                            "flexWrap": "wrap",
                        },
                    )
                ],
                show_divider=False,
                style={
                    "backgroundColor": "FFFFFF",
                },
            ).render()
        )
