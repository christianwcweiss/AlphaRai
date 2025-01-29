from typing import List

from quant_ui.theme.color import Color


class Palette:
    def __init__(self, colors: List[Color]) -> None:
        self._colors = colors

    @property
    def colors(self) -> List[Color]:
        return self._colors

    @staticmethod
    def create_gradient_palette(start_hex: str, end_hex: str, n_colors: int) -> "Palette":
        """
        Create a Palette of n_colors, going from start_hex to end_hex in a linear gradient.
        """

        # Helper to convert #RRGGBB to (R, G, B)
        def hex_to_rgb(h: str):
            return tuple(int(h[i : i + 2], 16) for i in (1, 3, 5))

        # Helper to convert (R, G, B) to #RRGGBB
        def rgb_to_hex(rgb: tuple):
            return "#{:02X}{:02X}{:02X}".format(*rgb)

        start_rgb = hex_to_rgb(start_hex)
        end_rgb = hex_to_rgb(end_hex)

        colors = []
        for i in range(n_colors):
            fraction = i / (n_colors - 1)  # goes from 0 to 1
            r = round(start_rgb[0] + fraction * (end_rgb[0] - start_rgb[0]))
            g = round(start_rgb[1] + fraction * (end_rgb[1] - start_rgb[1]))
            b = round(start_rgb[2] + fraction * (end_rgb[2] - start_rgb[2]))
            colors.append(Color(rgb_to_hex((r, g, b))))

        return Palette(colors)


TRADING_PALETTE = Palette.create_gradient_palette("#00FF00", "#FF0000", 10)
STANDARD_PALETTE = Palette.create_gradient_palette("#F7F7F7", "#252525", 10)
