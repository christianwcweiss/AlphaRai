PRIMARY_COLOR = "#00796b"
SECONDARY_COLOR = "#009688"
ACCENT_COLOR = "#e0f2f1"
BACKGROUND_COLOR = "#ffffff"
TEXT_COLOR = "#333333"
SUCCESS_COLOR = "#76FF03"
WARNING_COLOR = "#FFEB3B"
ERROR_COLOR = "#FF5252"

DARK_TEXT_COLOR = "#333333"
LIGHT_TEXT_COLOR = "#FFFFFF"

CHART_PALETTE = [
    "#009688",
    "#FF7043",
    "#29B6F6",
    "#AB47BC",
    "#66BB6A",
    "#FFCA28",
    "#8D6E63",
    "#EC407A",
    "#7E57C2",
]


def get_text_color(background_color: str) -> str:
    hex_color = background_color.lstrip("#")
    red, green, blue = int(hex_color[0:2], 16), int(hex_color[2:4], 16), int(hex_color[4:6], 16)

    luminance = 0.2126 * red + 0.7152 * green + 0.0722 * blue

    return DARK_TEXT_COLOR if luminance > 128 else LIGHT_TEXT_COLOR
