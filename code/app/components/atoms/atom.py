import abc
from typing import Any, Dict

from dash.development.base_component import Component


class Atom(abc.ABC):
    """Base class for all components in the application."""

    DEFAULT_STYLE: Dict[str, Any]

    @abc.abstractmethod
    def validate(self) -> None:
        """Validate the component's properties."""

    @abc.abstractmethod
    def render(self) -> Component:
        """Render and return the Dash layout component."""
