import abc

from dash.development.base_component import Component


class BasePage(abc.ABC):
    def __init__(
        self,
        title: str,
    ) -> None:
        self._title = title

    @abc.abstractmethod
    def render(self) -> Component:
        """Render and return the Dash layout component."""
        pass

    @property
    def layout(self) -> Component:
        """Exposes the layout, useful for Dash page registration."""
        return self.render()
