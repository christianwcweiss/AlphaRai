from dash import html
from typing import List, Union
from dash.development.base_component import Component

class MainContent(html.Div):
    def __init__(self, children: Union[Component, List[Component]], **kwargs):
        style = {
            "padding": "20px",
            "margin": "5px"
        }

        # Allow user styles to override default
        if "style" in kwargs:
            style.update(kwargs.pop("style"))

        super().__init__(children=children, style=style, **kwargs)