import abc
from typing import Any, Dict

from dash.development.base_component import Component


class Molecule(abc.ABC):  # pylint: disable=too-few-public-methods
    """Abstract base class for all molecules in the application."""

    STYLE: Dict[str, Any]

    @abc.abstractmethod
    def render(self, *args, **kwargs) -> Component:
        """Render and return the Dash layout component."""
