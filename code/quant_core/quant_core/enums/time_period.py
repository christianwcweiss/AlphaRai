from enum import Enum


class TimePeriod(Enum):
    MINUTE_5 = 5
    MINUTE_15 = 15
    MINUTE_30 = 30
    HOUR_1 = 60
    HOUR_4 = 60 * 4
    DAY = 60 * 24
    WEEK = 60 * 24 * 7

    def to_ig_period(self) -> str:
        return {
            TimePeriod.MINUTE_5: "MINUTE_5",
            TimePeriod.MINUTE_15: "MINUTE_15",
            TimePeriod.MINUTE_30: "MINUTE_30",
            TimePeriod.HOUR_1: "HOUR",
            TimePeriod.HOUR_4: "HOUR_4",
            TimePeriod.DAY: "DAY",
            TimePeriod.WEEK: "WEEK",
        }[self]
