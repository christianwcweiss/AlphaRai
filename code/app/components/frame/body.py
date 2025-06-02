from typing import List, Union

from dash import html
from dash.development.base_component import Component


class PageBody(html.Div):  # pylint: disable=too-few-public-methods
    """Page body component for the application."""

    def __init__(self, children: Union[Component, List[Component]], **kwargs):
        # You can customize these default styles as needed
        style = {
            "padding": "40px",
            "margin": "20px auto",
            "maxWidth": "1200px",
            "backgroundColor": "#ffffff",
            "borderRadius": "10px",
            "boxShadow": "0 4px 12px rgba(0, 0, 0, 0.1)",
            "minHeight": "80vh",
        }

        # Merge user-supplied styles if any
        if "style" in kwargs:
            style.update(kwargs.pop("style"))

        super().__init__(children=children, style=style, **kwargs)
