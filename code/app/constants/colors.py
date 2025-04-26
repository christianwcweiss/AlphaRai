# Color Palette
PRIMARY_COLOR = "#0D47A1"  # Dark Blue
SECONDARY_COLOR = "#1565C0"  # Medium Blue
ACCENT_COLOR = "#1976D2"  # Blue
BACKGROUND_COLOR = "#E3F2FD"  # Light Blue Background
TEXT_COLOR = "#333333"  # Dark Gray (For Text)
NAVBAR_COLOR = "#1E88E5"  # Blue Navbar
SUCCESS_COLOR = "#76FF03"  # Bright Green (Success)
WARNING_COLOR = "#FFEB3B"  # Yellow (for warnings)
ERROR_COLOR = "#FF5252"  # Light Red (for errors)

# Text Color Variables
DARK_TEXT_COLOR = "#333333"  # Dark text for light backgrounds
LIGHT_TEXT_COLOR = "#FFFFFF"  # Light text for dark backgrounds


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
