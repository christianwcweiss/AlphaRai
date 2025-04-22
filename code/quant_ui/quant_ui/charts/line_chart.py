from typing import List, Optional

import pandas as pd

from quant_ui.charts.chart import Chart
import plotly.graph_objects as go


class LineChart(Chart):
    def plot(self, data_frame: pd.DataFrame, x_col: str, y_col: List[str], groupby: Optional[str] = None) -> go.Figure:
        # If groupby is provided, we group the data first
        if groupby:
            grouped_data = data_frame.groupby(groupby)
        else:
            grouped_data = [(None, data_frame)]  # No grouping, single group

        fig = go.Figure()

        # For each group in the grouped data (if any), plot the data
        for group_name, group_data in grouped_data:
            for y in y_col:
                fig.add_trace(
                    go.Scatter(
                        x=group_data[x_col],
                        y=group_data[y],
                        mode='lines',  # Use lines for a line chart
                        name=f"{group_name} - {y}" if group_name else y
                    )
                )

        # Layout customizations
        layout_kwargs = {
            "title": self.title,
            "title_x": 0.5,  # Center title
            "template": "plotly_white",  # Set a clean, light background
            "plot_bgcolor": self.__BACKGROUND__,  # Set fixed background color for the plot
            "xaxis_title": x_col if self.show_x_title else "",
            "yaxis_title": ", ".join(y_col) if self.show_y_title else "",
            "showlegend": self.show_legend,
            "annotations": [
                dict(
                    x=0.5,
                    y=1.05,
                    xref="paper",
                    yref="paper",
                    text=self.subtitle,
                    showarrow=False,
                    font=dict(size=12, color="black"),
                    align="center"
                )
            ]
        }

        fig.update_layout(**layout_kwargs)

        return fig