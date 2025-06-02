import pytest
from constants.colors import (
    ACCENT_COLOR,
    BACKGROUND_COLOR,
    DARK_TEXT_COLOR,
    ERROR_COLOR,
    LIGHT_TEXT_COLOR,
    PRIMARY_COLOR,
    SECONDARY_COLOR,
    SUCCESS_COLOR,
    TEXT_COLOR,
    WARNING_COLOR,
    get_text_color,
)


class TestColors:
    @pytest.mark.parametrize(
        "color, expected_text_color",
        [
            (PRIMARY_COLOR, LIGHT_TEXT_COLOR),
            (SECONDARY_COLOR, LIGHT_TEXT_COLOR),
            (ACCENT_COLOR, DARK_TEXT_COLOR),
            (BACKGROUND_COLOR, DARK_TEXT_COLOR),
            (TEXT_COLOR, LIGHT_TEXT_COLOR),
            (SUCCESS_COLOR, DARK_TEXT_COLOR),
            (WARNING_COLOR, DARK_TEXT_COLOR),
            (ERROR_COLOR, LIGHT_TEXT_COLOR),
        ],
    )
    def test_colors(self, color: str, expected_text_color: str) -> None:
        text_color = get_text_color(color)

        assert text_color == expected_text_color, f"Expected {expected_text_color} for {color}, but got {text_color}"
