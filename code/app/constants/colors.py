# Color Palette
PRIMARY_COLOR = "#00796b"
SECONDARY_COLOR = "#009688"
ACCENT_COLOR = "#e0f2f1"
BACKGROUND_COLOR = "#E3F2FD"
TEXT_COLOR = "#333333"
SUCCESS_COLOR = "#76FF03"
WARNING_COLOR = "#FFEB3B"
ERROR_COLOR = "#FF5252"

# Text Color Variables
DARK_TEXT_COLOR = "#333333"  # Dark text for light backgrounds
LIGHT_TEXT_COLOR = "#FFFFFF"  # Light text for dark backgrounds

# Chart
CHART_PALETTE = [
    "#009688",  # Primary Teal
    "#FF7043",  # Warm Orange
    "#29B6F6",  # Light Blue
    "#AB47BC",  # Violet Purple
    "#66BB6A",  # Green
    "#FFCA28",  # Yellow/Gold
    "#8D6E63",  # Brown Grey
    "#EC407A",  # Pink Rose
    "#7E57C2",  # Deep Purple
]


# Function to determine text color based on background brightness
def get_text_color(background_color: str) -> str:
    # Convert hex color to RGB
    hex_color = background_color.lstrip("#")
    r, g, b = int(hex_color[0:2], 16), int(hex_color[2:4], 16), int(hex_color[4:6], 16)

    # Calculate the luminance to decide whether to use dark or light text
    luminance = 0.2126 * r + 0.7152 * g + 0.0722 * b

    # If luminance is greater than 128 (midpoint), use dark text, otherwise light text
    if luminance > 128:
        return DARK_TEXT_COLOR  # Use dark text color for light backgrounds
    else:
        return LIGHT_TEXT_COLOR  # Use light text color for dark backgrounds
