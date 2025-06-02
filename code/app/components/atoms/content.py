from typing import List, Union

from dash import html
from dash.development.base_component import Component


class MainContent(html.Div):  # pylint: disable=too-few-public-methods
    """Main content area of the application."""

    def __init__(self, children: Union[Component, List[Component]], **kwargs):
        style = {"padding": "20px", "margin": "5px"}

        if "style" in kwargs:
            style.update(kwargs.pop("style"))

        super().__init__(children=children, style=style, **kwargs)
