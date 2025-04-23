from dash import html
from typing import Optional

from constants import colors


class AlphaButton(html.Div):
    def __init__(
        self,
        label: str,
        href: Optional[str] = None,
        width: Optional[str] = None,
        height: Optional[str] = None,
        color: Optional[str] = None,
        id: Optional[str] = None,
        n_clicks: Optional[int] = 0,
        **kwargs
    ):
        button_color = color or colors.PRIMARY_COLOR

        base_style = {
            "backgroundColor": button_color,
            "color": "white",
            "padding": "0.75rem 1.5rem",
            "borderRadius": "0.5rem",
            "textAlign": "center",
            "cursor": "pointer",
            "fontWeight": "600",
            "fontSize": "1rem",
            "transition": "background-color 0.2s ease",
            "userSelect": "none",
            "display": "inline-block",
        }

        if width:
            base_style["width"] = width
        if height:
            base_style["height"] = height

        button_content = html.Div(label, style=base_style)

        if href:
            super().__init__(
                children=html.A(
                    href=href,
                    children=button_content,
                    style={"textDecoration": "none", "color": "inherit", "display": "inline-block"},
                ),
                id=id,
                **kwargs
            )
        else:
            super().__init__(children=button_content, id=id, n_clicks=n_clicks, **kwargs)
