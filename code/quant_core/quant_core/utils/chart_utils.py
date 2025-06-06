import pandas as pd
from quant_core.enums.time_period import TimePeriod
from quant_core.enums.trade_direction import TradeDirection


def calculate_stop_loss(direction: TradeDirection, entry_price: float, distance: float) -> float:
    """Calculate stop loss price based on direction and entry price."""
    return entry_price - distance if direction.normalize() is TradeDirection.LONG else entry_price + distance


def calculate_take_profit(direction: TradeDirection, entry_price: float, distance: float) -> float:
    """Calculate take profit price based on direction and entry price."""
    return entry_price + distance if direction.normalize() is TradeDirection.LONG else entry_price - distance


def get_data_frame_period(data_frame: pd.DataFrame) -> TimePeriod:
    """Get the most frequent time period from the DataFrame."""
    data_frame["date_diff"] = data_frame["date"].diff()
    diff_series = data_frame["date_diff"].dropna()

    counts = diff_series.value_counts()
    most_frequent_diff = counts.index[0]
    count_of_most_frequent_diff = counts.iloc[0]

    percentage = count_of_most_frequent_diff / len(diff_series)
    assert percentage >= 0.75, (
        f"The most frequent difference appears in only {percentage:.2%} of rows, " "which is below the 75% threshold."
    )

    most_frequent_diff_in_minutes = most_frequent_diff.total_seconds() / 60

    return TimePeriod(most_frequent_diff_in_minutes)


def check_df_sorted(data_frame: pd.DataFrame) -> None:
    """Check if the DataFrame is sorted by date."""
    if "date" not in data_frame or not data_frame["date"].is_monotonic_increasing:
        raise AssertionError("DataFrame 'date' column does not exist or must be sorted ascending.")


def check_enough_rows(data_frame: pd.DataFrame) -> None:
    """Check if the DataFrame has enough rows."""
    if len(data_frame) < 1000:
        raise AssertionError("DataFrame must have at least 1000 rows.")
