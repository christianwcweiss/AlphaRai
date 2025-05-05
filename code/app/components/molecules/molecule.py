import abc
from typing import Any, Dict

from dash.development.base_component import Component


class Molecule(abc.ABC):
    STYLE: Dict[str, Any]

    @abc.abstractmethod
    def render(self) -> Component:
        """Render and return the Dash layout component."""
        pass
