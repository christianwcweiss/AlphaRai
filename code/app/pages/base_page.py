import abc
from typing import Any, List, Dict
from dash.development.base_component import Component


class BasePage(abc.ABC):
    def __init__(
        self,
        title: str,
        *args: List[Any],
        **kwargs: Dict[str, Any],
    ) -> None:
        self.title = title
        self.args = args
        self.kwargs = kwargs

    @abc.abstractmethod
    def render(self) -> Component:
        """Render and return the Dash layout component."""
        pass

    @property
    def layout(self) -> Component:
        """Exposes the layout, useful for Dash page registration."""
        return self.render()
