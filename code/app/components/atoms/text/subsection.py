from dash import html

from constants import colors


class SubsectionHeader(html.Div):
    def __init__(self, title: str, **kwargs):
        # Extract and merge any existing style passed through kwargs
        user_style = kwargs.pop("style", {})
        merged_style = {"paddingTop": "1rem", "marginTop": "1rem", **user_style}

        super().__init__(
            children=[
                html.H3(title, style={"marginTop": "0.5rem", "color": colors.SECONDARY_COLOR, "fontSize": "1.25rem"})
            ],
            style=merged_style,
            **kwargs
        )
