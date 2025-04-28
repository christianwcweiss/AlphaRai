from typing import Optional, Union, List

from dash import html
from dash.development.base_component import Component

from components.atoms.atom import Atom
from components.atoms.text.paragraph import Paragraph
from constants import colors
from exceptions.ui import ComponentPropertyError


class AlphaCard(Atom):
    DEFAULT_STYLE = {
        "padding": "1.5rem",
        "borderRadius": "0.5rem",
        "backgroundColor": colors.PRIMARY_COLOR,
        "boxShadow": "0 4px 8px rgba(0, 0, 0, 0.05)",
        "marginBottom": "1rem",
        "transition": "transform 0.2s ease",
        "display": "flex",
        "flexDirection": "column",
        "justifyContent": "flex-start",
    }

    def __init__(
        self,
        children: Union[html.Div, List[html.Div]],
        title: Optional[str] = None,
        subtitle: Optional[str] = None,
        href: Optional[str] = None,
        aspect_ratio: Optional[str] = None,
        height: Optional[str] = None,
        width: Optional[str] = None,
    ) -> None:
        self._children = children
        self._title = title
        self._subtitle = subtitle
        self._href = href
        self._aspect_ratio = aspect_ratio
        self._height = height
        self._width = width

        self.validate()

    def validate(self) -> None:
        if self._aspect_ratio is not None and self._width is not None and self._height is not None:
            raise ComponentPropertyError(
                "You cannot set both aspect_ratio and width/height properties at the same time."
            )

    def _render_header(self) -> html.Div:
        header_items = []

        if self._title:
            header_items.append(
                html.H4(
                    children=self._title,
                    style={"textAlign": "center", "marginTop": "0px", "color": colors.LIGHT_TEXT_COLOR},
                )
            )

        if self._subtitle:
            header_items.append(
                Paragraph(
                    text=self._subtitle,
                )
            )

        return html.Div(header_items)

    def _render_children(self) -> List[Component]:
        children = self._children
        if isinstance(children, list):
            return children
        else:
            return [children]

    def _render_card(
        self,
        header_section: html.Div,
        main_section: List[Component],
    ) -> Union[html.Div, html.A]:
        card_style = self.DEFAULT_STYLE
        card_style["width"] = self._width if self._width else None
        card_style["height"] = self._height if self._height else None
        card_style["aspectRatio"] = self._aspect_ratio if self._aspect_ratio else None
        card_style["cursor"] = "pointer" if self._href else None

        card_style = {k: v for k, v in card_style.items() if v is not None}

        card_div = html.Div(
            children=[header_section] + main_section,
            style=card_style,
        )

        link_component = (
            (
                html.Div(
                    children=html.A(
                        href=self._href,
                        children=card_div,
                        style={
                            "textDecoration": "none",
                            "color": "inherit",
                            "display": "block",
                            "height": "100%",
                            "width": "100%",
                        },
                    ),
                )
            )
            if self._href
            else None
        )

        return link_component if link_component else card_div

    def render(self) -> html.Div:
        header_section = self._render_header()
        main_section = self._render_children()

        return self._render_card(header_section, main_section)
