from enum import Enum


class TimePeriod(Enum):
    """Enum for time periods in minutes."""

    MINUTE_5 = 5
    MINUTE_15 = 15
    MINUTE_30 = 30
    HOUR_1 = 60
    HOUR_4 = 60 * 4
    DAY = 60 * 24
    WEEK = 60 * 24 * 7
