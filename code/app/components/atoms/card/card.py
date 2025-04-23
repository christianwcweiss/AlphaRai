from typing import Optional, Union, List
from dash import html

from components.atoms.text.paragraph import Paragraph
from components.atoms.text.subsubsection import SubSubsectionHeader
from constants import colors


class AlphaCard(html.Div):
    def __init__(
        self,
        children: Union[html.Div, List[html.Div]],
        title: Optional[str] = None,
        subtitle: Optional[str] = None,
        href: Optional[str] = None,
        aspect_ratio: Optional[str] = None,
        height: Optional[str] = None,
        width: Optional[str] = None,
        **kwargs
    ):
        card_children = []

        # Header section with centered title and subtitle
        if title or subtitle:
            header_items = []

            if title:
                header_items.append(
                    html.H4(
                        children=title,
                        style={"textAlign": "center", "marginTop": "0px", "color": colors.LIGHT_TEXT_COLOR},
                    )
                )

            if subtitle:
                header_items.append(
                    Paragraph(
                        text=subtitle,
                    )
                )

            header_section = html.Div(header_items)

            divider = html.Hr(style={"border": "none", "borderTop": "1px solid #ddd", "margin": "1rem 0"})

            card_children.extend([header_section, divider])

        # Add main content
        if isinstance(children, list):
            card_children.extend(children)
        else:
            card_children.append(children)

        # Build card style
        card_style = {
            "padding": "1.5rem",
            "borderRadius": "0.5rem",
            "backgroundColor": colors.PRIMARY_COLOR,
            "boxShadow": "0 4px 8px rgba(0, 0, 0, 0.05)",
            "marginBottom": "1rem",
            "cursor": "pointer" if href else "default",
            "transition": "transform 0.2s ease",
            "display": "flex",
            "flexDirection": "column",
            "justifyContent": "flex-start",
        }

        if width:
            card_style["width"] = width
        if height:
            card_style["height"] = height
        if aspect_ratio:
            card_style["aspectRatio"] = aspect_ratio

        card_div = html.Div(children=card_children, style=card_style, className="alpha-card")

        # Wrap in <a> if href is provided
        if href:
            super().__init__(
                children=html.A(
                    href=href,
                    children=card_div,
                    style={
                        "textDecoration": "none",
                        "color": "inherit",
                        "display": "block",
                        "height": "100%",
                        "width": "100%",
                    },
                ),
                style={"height": height, "width": width} if height or width else {},
                **kwargs
            )
        else:
            super().__init__(children=card_div, **kwargs)
