import abc
from typing import Any, Dict

from dash.development.base_component import Component


class Atom(abc.ABC):
    DEFAULT_STYLE: Dict[str, Any]

    @abc.abstractmethod
    def render(self) -> Component:
        """Render and return the Dash layout component."""
        pass
