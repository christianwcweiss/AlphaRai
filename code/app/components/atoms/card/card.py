from typing import List, Optional, Union

from components.atoms.atom import Atom
from components.atoms.divider.divider import Divider
from components.atoms.text.paragraph import Paragraph
from constants import colors
from dash import html
from dash.development.base_component import Component


class AlphaCardHeader(Atom):
    """Header for the AlphaCard component."""

    def __init__(self, children: Union[Component, List[Component]]) -> None:
        self.children = children

    def validate(self) -> None:
        return

    def render(self) -> html.Div:
        """Renders the header of the card."""
        return html.Div(
            children=self.children if isinstance(self.children, list) else [self.children],
            style={
                "display": "flex",
                "flexDirection": "column",
                "alignItems": "center",
                "justifyContent": "center",
                "width": "100%",
            },
        )


class AlphaCardBody(Atom):
    """Body for the AlphaCard component."""

    def __init__(self, children: Union[Component, List[Component]]):
        self.children = children

    def validate(self) -> None:
        return

    def render(self) -> html.Div:
        """Renders the body of the card."""
        return html.Div(
            children=self.children if isinstance(self.children, list) else [self.children],
            style={
                "width": "100%",
                "flex": "1",
            },
        )


class AlphaCard(Atom):  # pylint: disable=too-many-instance-attributes
    """A card component for displaying content in a visually appealing way."""

    DEFAULT_STYLE = {
        "padding": "1.5rem",
        "borderRadius": "0.5rem",
        "border": "1px solid rgba(0, 0, 0, 0.1)",
        "backgroundColor": colors.PRIMARY_COLOR,
        "boxShadow": "0 4px 8px rgba(0, 0, 0, 0.05)",
        "transition": "transform 0.2s ease",
        "display": "flex",
        "flexDirection": "column",
        "justifyContent": "flex-start",
    }

    def __init__(  # pylint: disable=too-many-arguments, too-many-positional-arguments
        self,
        children: Union[html.Div, List[html.Div]] = None,
        title: Optional[str] = None,
        subtitle: Optional[str] = None,
        href: Optional[str] = None,
        aspect_ratio: Optional[str] = None,
        height: Optional[str] = None,
        width: Optional[str] = None,
        header: Optional[html.Div] = None,
        body: Optional[html.Div] = None,
        style: Optional[dict] = None,
        show_divider: bool = True,
    ) -> None:
        self._children = children
        self._title = title
        self._subtitle = subtitle
        self._href = href
        self._aspect_ratio = aspect_ratio
        self._height = height
        self._width = width
        self._custom_header = header
        self._custom_body = body
        self._style = style
        self._show_divider = show_divider

        self.validate()

    def validate(self) -> None:
        """Validates the card properties."""

    def _render_header(self) -> html.Div:
        if self._custom_header:
            return self._custom_header
        header_items = []
        if self._title:
            header_items.append(
                html.H4(
                    children=self._title,
                    style={"textAlign": "center", "marginTop": "0px", "color": colors.TEXT_ON_SECONDARY},
                )
            )
        if self._subtitle:
            header_items.append(Paragraph(text=self._subtitle).render())

        return html.Div(header_items)

    def _render_children(self) -> List[Component]:
        if self._custom_body:
            return [self._custom_body]
        if isinstance(self._children, list):
            return self._children
        return [self._children]

    def _render_card(
        self,
        header_section: html.Div,
        main_section: List[Component],
    ) -> Union[html.Div, html.A]:
        card_style = self.DEFAULT_STYLE | (self._style if self._style else {})
        card_style["width"] = self._width if self._width else None
        card_style["height"] = self._height if self._height else None
        card_style["aspectRatio"] = self._aspect_ratio if self._aspect_ratio else None
        card_style["cursor"] = "pointer" if self._href else None
        card_style = {k: v for k, v in card_style.items() if v is not None}

        children = [header_section]

        if self._show_divider:
            children.append(Divider().render())

        children += main_section

        card_div = html.Div(children=children, style=card_style)

        if self._href:
            return html.Div(
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
                )
            )

        return card_div

    def render(self) -> html.Div:
        """Renders the card component."""
        header_section = self._render_header()
        main_section = self._render_children()

        return self._render_card(header_section, main_section)
