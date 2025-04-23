from dash import html

from constants import colors


class SubSubsectionHeader(html.Div):
    def __init__(self, title: str, **kwargs):
        user_style = kwargs.pop("style", {})
        merged_style = {"paddingTop": "1rem", "marginTop": "1rem", **user_style}

        super().__init__(
            children=[html.H4(title, style={"color": colors.SECONDARY_COLOR, "fontSize": "1.0rem"})],
            style=merged_style,
            **kwargs
        )
