from typing import Optional

from dash import html

from constants import colors


class SectionHeader(html.Div):
    def __init__(self, title: str, subtitle: Optional[str] = None, **kwargs):
        super().__init__(
            children=[
                html.H2(title, style={"marginBottom": "0.25rem", "color": colors.PRIMARY_COLOR}),
                (
                    html.P(subtitle, style={"marginTop": "0", "color": colors.TEXT_COLOR, "fontSize": "1rem"})
                    if subtitle
                    else None
                ),
            ],
            style={
                "paddingBottom": "1.5rem",
                "marginBottom": "1rem",
                "borderBottom": f"2px solid {colors.PRIMARY_COLOR}",
            },
            **kwargs,
        )
