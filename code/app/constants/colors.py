# Primary Theme Colors
PRIMARY_COLOR = "#6200EE"  # Material Indigo 500
PRIMARY_VARIANT = "#3700B3"  # Material Indigo 700
SECONDARY_COLOR = "#03DAC6"  # Material Teal 200
SECONDARY_VARIANT = "#018786"  # Material Teal 700
ACCENT_COLOR = "#FF4081"  # Accent Pink A200

# Background & Surface
BACKGROUND_COLOR = "#F5F5F5"  # Light grey background
SURFACE_COLOR = "#FFFFFF"  # Card or surface color
ELEVATED_SURFACE_COLOR = "#FAFAFA"
SHADOW_COLOR = "rgba(0, 0, 0, 0.2)"

# Border & Dividers
DIVIDER_COLOR = "#E0E0E0"
BORDER_COLOR = "#DDDDDD"

# Text Colors
TEXT_PRIMARY = "#212121"  # High-emphasis text
TEXT_SECONDARY = "#757575"  # Medium-emphasis text
TEXT_DISABLED = "#BDBDBD"  # Disabled text
TEXT_ON_PRIMARY = "#FFFFFF"
TEXT_ON_SECONDARY = "#000000"
TEXT_ON_ACCENT = "#FFFFFF"
PLACEHOLDER_TEXT = "#9E9E9E"
TEXT_WHITE = "#FFFFFF"
TEXT_BLACK = "#000000"

# Status Colors
SUCCESS_COLOR = "#4CAF50"
WARNING_COLOR = "#FFC107"
ERROR_COLOR = "#F44336"
INFO_COLOR = "#2196F3"

# Greyscale
GREY_100 = "#F5F5F5"
GREY_200 = "#EEEEEE"
GREY_300 = "#E0E0E0"
GREY_400 = "#BDBDBD"
GREY_500 = "#9E9E9E"
GREY_600 = "#757575"
GREY_700 = "#616161"
GREY_800 = "#424242"
GREY_900 = "#212121"

# Chart Colors (Material-inspired)
CHART_PALETTE = [
    "#6200EE",  # Primary
    "#03DAC6",  # Secondary
    "#F44336",  # Error
    "#FF9800",  # Orange
    "#4CAF50",  # Green
    "#2196F3",  # Blue
    "#9C27B0",  # Purple
    "#FFEB3B",  # Yellow
    "#795548",  # Brown
]

# Buttons
BUTTON_PRIMARY_BG = PRIMARY_COLOR
BUTTON_PRIMARY_TEXT = TEXT_ON_PRIMARY
BUTTON_SECONDARY_BG = SECONDARY_COLOR
BUTTON_SECONDARY_TEXT = TEXT_ON_SECONDARY
BUTTON_DISABLED_BG = GREY_300
BUTTON_DISABLED_TEXT = GREY_500

# Input Fields
INPUT_BORDER_COLOR = GREY_300
INPUT_FOCUS_COLOR = PRIMARY_COLOR
INPUT_ERROR_COLOR = ERROR_COLOR
INPUT_PLACEHOLDER_COLOR = PLACEHOLDER_TEXT

# Alerts
ALERT_SUCCESS_BG = "#E8F5E9"
ALERT_WARNING_BG = "#FFF8E1"
ALERT_ERROR_BG = "#FFEBEE"
ALERT_INFO_BG = "#E3F2FD"


def get_text_color(background_color: str) -> str:
    """Get the appropriate text color based on the background color."""
    hex_color = background_color.lstrip("#")
    red, green, blue = int(hex_color[0:2], 16), int(hex_color[2:4], 16), int(hex_color[4:6], 16)

    luminance = 0.2126 * red + 0.7152 * green + 0.0722 * blue

    return TEXT_BLACK if luminance > 150 else TEXT_WHITE
