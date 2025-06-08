import pytest
from constants.colors import (
    ACCENT_COLOR,
    BACKGROUND_COLOR,
    ERROR_COLOR,
    PRIMARY_COLOR,
    SECONDARY_COLOR,
    SUCCESS_COLOR,
    TEXT_BLACK,
    TEXT_WHITE,
    WARNING_COLOR,
    get_text_color,
)


class TestColors:
    @pytest.mark.parametrize(
        "color, expected_text_color",
        [
            (PRIMARY_COLOR, TEXT_WHITE),
            (SECONDARY_COLOR, TEXT_BLACK),
            (ACCENT_COLOR, TEXT_WHITE),
            (BACKGROUND_COLOR, TEXT_BLACK),
            (SUCCESS_COLOR, TEXT_WHITE),
            (WARNING_COLOR, TEXT_BLACK),
            (ERROR_COLOR, TEXT_WHITE),
        ],
    )
    def test_colors(self, color: str, expected_text_color: str) -> None:
        text_color = get_text_color(color)

        assert text_color == expected_text_color, f"Expected {expected_text_color} for {color}, but got {text_color}"
