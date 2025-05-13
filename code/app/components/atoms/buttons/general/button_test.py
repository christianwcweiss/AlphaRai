import pytest
from dash import html

from components.atoms.buttons.general.button import AlphaButton
from exceptions.ui import ComponentPropertyError
from quant_dev.builder import Builder


class TestAlphaButton:
    def test_empty_label(self) -> None:
        with pytest.raises(ComponentPropertyError):
            AlphaButton(label="")

    def test_no_id_set(self) -> None:
        button = AlphaButton(label="Test Button")

        assert button._id == "button-testbutton"

    def test_override_style(self) -> None:
        default_style = AlphaButton.DEFAULT_STYLE
        modified_style = {k: Builder.build_random_string(8) for k in default_style.keys()}

        button = AlphaButton(label="Test Button", style=modified_style)

        assert button._style == modified_style

    def test_render_button_without_href(self) -> None:
        button = AlphaButton(label="Click Me")

        rendered = button.render()

        assert isinstance(rendered, html.Div)
        assert isinstance(rendered.children, html.Button)
        assert rendered.children.children == "Click Me"
        assert rendered.children.id.startswith("button-clickme")
        assert rendered.children.style["backgroundColor"]

    def test_render_button_with_custom_id(self) -> None:
        button = AlphaButton(label="Click Me", button_id="custom-id")

        rendered = button.render()

        assert rendered.children.id == "custom-id"

    def test_render_button_with_href(self) -> None:
        button = AlphaButton(label="Visit", href="https://example.com")

        rendered = button.render()

        assert isinstance(rendered, html.Div)
        link = rendered.children
        assert isinstance(link, html.A)
        assert link.href == "https://example.com"
        assert isinstance(link.children, html.Button)
        assert link.children.children == "Visit"

    def test_render_button_with_custom_style(self) -> None:
        custom_style = {"backgroundColor": "red"}
        button = AlphaButton(label="Styled", style=custom_style)

        rendered = button.render()

        assert rendered.children.style["backgroundColor"] == "red"
        assert "border" in rendered.children.style
