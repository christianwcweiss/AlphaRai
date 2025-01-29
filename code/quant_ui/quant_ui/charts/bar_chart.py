import os

import pandas as pd
from bokeh.io import output_file
from bokeh.models import ColumnDataSource
from bokeh.plotting import figure, show, save

from quant_ui.enums import Orientation
from quant_ui.theme.palette import Palette


class BarChart:
    def __init__(
        self, data_frame: pd.DataFrame, palette: Palette, orientation: Orientation = Orientation.VERTICAL
    ) -> None:
        self._data_frame = data_frame
        self._palette = palette
        self._orientation = orientation

    def _plot_bar(
        self,
        x_col: str,
        y_col: str,
        orientation: Orientation = Orientation.VERTICAL,
        title: str = "Bar Chart",
    ) -> None:
        x_values = self._data_frame[x_col].tolist()
        y_values = self._data_frame[y_col].tolist()

        colors = [self._palette.colors[0].hex_code if y >= 0 else self._palette.colors[-1].hex_code for y in y_values]

        source = ColumnDataSource(data={"x": x_values, "y": y_values, "color": colors})

        if orientation == Orientation.VERTICAL:
            p = figure(
                x_range=[str(x) for x in x_values],
                title=title,
                toolbar_location="above",
                x_axis_label=x_col,
                y_axis_label=y_col,
            )
            p.vbar(x="x", top="y", width=0.8, color="color", source=source)
            p.xgrid.grid_line_color = None
        else:
            p = figure(
                y_range=[str(y) for y in y_values],
                title=title,
                toolbar_location="above",
                x_axis_label=x_col,
                y_axis_label=y_col,
            )
            p.hbar(y="y", right="x", height=0.8, color="color", source=source)
            p.ygrid.grid_line_color = None

        self._fig = p

    def plot(self, x_col: str, y_col: str, title: str, orientation: Orientation) -> None:
        self._plot_bar(x_col=x_col, y_col=y_col, title=title, orientation=orientation)

    def show(self) -> None:
        if self._fig is None:
            raise ValueError("No figure to show. Create a chart first (plot_vertical or plot_horizontal).")

        show(self._fig)

    def save_fig(self, directory: str, filename: str) -> None:
        if self._fig is None:
            raise ValueError("No figure to save. Create a chart first (plot_vertical or plot_horizontal).")

        output_file(os.path.join(directory, filename))
        save(self._fig)
