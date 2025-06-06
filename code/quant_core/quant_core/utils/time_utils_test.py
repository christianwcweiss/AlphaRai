import pytest
from quant_core.enums.weekday import Weekday
from quant_core.utils.time_utils import (
    convert_minutes_since_week_started_to_time,
    convert_time_data_to_minutes_since_week_started,
)


@pytest.mark.parametrize(
    "weekday,hour,minutes,expected",
    [
        (Weekday.MONDAY, 3, 0, 3 * 60),
        (Weekday.TUESDAY, 12, 30, 24 * 60 + 12 * 60 + 30),
        (Weekday.WEDNESDAY, 23, 59, 48 * 60 + 23 * 60 + 59),
        (Weekday.THURSDAY, 0, 0, 72 * 60),
        (Weekday.FRIDAY, 6, 15, 96 * 60 + 6 * 60 + 15),
    ],
)
def test_time_since_week_started_conversions(weekday: Weekday, hour: int, minutes: int, expected: int) -> None:
    """Test the conversion of time data to minutes since the week started."""

    minutes_since_start = convert_time_data_to_minutes_since_week_started(weekday, hour, minutes)

    assert minutes_since_start == expected, f"Expected {expected}, but got {minutes_since_start}."

    reverted_weekday, reverted_hour, reverted_minutes = convert_minutes_since_week_started_to_time(minutes_since_start)

    assert reverted_weekday == weekday, f"Expected weekday {weekday}, but got {reverted_weekday}."
    assert reverted_hour == hour, f"Expected hour {hour}, but got {reverted_hour}."
    assert reverted_minutes == minutes, f"Expected minutes {minutes}, but got {reverted_minutes}."
