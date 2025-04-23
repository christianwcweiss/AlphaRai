from dash import html

from constants import colors


class Paragraph(html.P):
    def __init__(self, text: str, **kwargs):
        super().__init__(
            children=text,
            style={
                "marginTop": "0.25rem",
                "marginBottom": "0.75rem",
                "color": colors.TEXT_COLOR,
                "fontSize": "0.95rem",
                "lineHeight": "1.5",
            },
            **kwargs
        )
