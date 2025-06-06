import dash_bootstrap_components as dbc
from components.atoms.atom import Atom
from dash import html


class AlphaModal(Atom):  # pylint: disable=too-few-public-methods, too-many-instance-attributes
    """A modal component for Dash applications."""

    def __init__(  # pylint: disable=too-many-arguments, too-many-positional-arguments
        self,
        modal_id: str,
        title: str,
        body_content: html.Div,
        confirm_id: str,
        cancel_id: str,
        confirm_label: str = "Save",
        cancel_label: str = "Cancel",
        confirm_color: str = "success",
        cancel_color: str = "secondary",
        centered: bool = True,
        size: str = "md",  # md, lg, xl
    ) -> None:
        self._modal_id = modal_id
        self._title = title
        self._body_content = body_content
        self._confirm_id = confirm_id
        self._cancel_id = cancel_id
        self._confirm_label = confirm_label
        self._cancel_label = cancel_label
        self._confirm_color = confirm_color
        self._cancel_color = cancel_color
        self._centered = centered
        self._size = size

        self.validate()

    def validate(self) -> None:
        if not self._modal_id:
            raise ValueError("Modal must have an ID.")

    def render(self) -> dbc.Modal:
        return dbc.Modal(
            id=self._modal_id,
            is_open=False,
            centered=self._centered,
            size=self._size,
            children=[
                dbc.ModalHeader(dbc.ModalTitle(self._title)),
                dbc.ModalBody(self._body_content),
                dbc.ModalFooter(
                    [
                        dbc.Button(self._confirm_label, id=self._confirm_id, color=self._confirm_color),
                        dbc.Button(self._cancel_label, id=self._cancel_id, color=self._cancel_color, className="ms-2"),
                    ]
                ),
            ],
        )
