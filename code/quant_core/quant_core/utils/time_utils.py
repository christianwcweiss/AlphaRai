from datetime import datetime
from typing import Union

import pytz
from croniter import croniter
from quant_core.enums.weekday import Weekday


def is_valid_cron(cron_expr: str) -> bool:
    """
    Returns True if the cron expression is valid, False otherwise.
    """
    try:
        croniter(cron_expr, datetime.now())
        return True
    except (ValueError, KeyError):
        return False


def describe_cron(cron: str, tz: str = "UTC") -> str:
    """Describe the next run time of a cron expression."""
    try:
        now = datetime.now(pytz.timezone(tz))
        itr = croniter(cron, now)

        next_time_raw: Union[float, datetime] = itr.get_next()  # no type arg, just get raw
        if isinstance(next_time_raw, float):
            next_time = datetime.fromtimestamp(next_time_raw, tz=pytz.timezone(tz))
        else:
            next_time = next_time_raw

        delta = next_time - now
        seconds = int(delta.total_seconds())

        if seconds < 0:
            return f"Cron is valid but next run was in the past ({next_time.strftime('%Y-%m-%d %H:%M')})"
        if seconds < 60:
            return f"Next run in {seconds} sec (at {next_time.strftime('%Y-%m-%d %H:%M')})"
        if seconds < 3600:
            return f"Next run in {seconds // 60} min (at {next_time.strftime('%Y-%m-%d %H:%M')})"

        return f"Next run at {next_time.strftime('%Y-%m-%d %H:%M')}"

    except Exception as error:  # pylint: disable=broad-exception-caught
        return f"Invalid cron: {error}"


def convert_time_data_to_minutes_since_week_started(weekday: Weekday, hour: int, minute: int) -> int:
    """
    Convert weekday, hour, and minute into seconds since the start of the week.
    """
    if not isinstance(weekday, Weekday):
        raise ValueError("weekday must be an instance of Weekday enum")

    if not 0 <= hour < 24 or not 0 <= minute < 60:
        raise ValueError("hour must be between 0 and 23, minute must be between 0 and 59")

    minutes_since_week_started = weekday.to_number() * 24 * 60 + hour * 60 + minute

    return minutes_since_week_started


def convert_minutes_since_week_started_to_time(minutes: int) -> tuple[Weekday, int, int]:
    """
    Convert minutes since the start of the week into weekday, hour, and minute.
    """
    if not isinstance(minutes, int) or minutes < 0:
        raise ValueError("minutes must be a non-negative integer")

    total_minutes_in_week = 7 * 24 * 60
    minutes = minutes % total_minutes_in_week  # wrap around if exceeds a week

    weekday_number = minutes // (24 * 60)
    remaining_minutes = minutes % (24 * 60)

    hour = remaining_minutes // 60
    minute = remaining_minutes % 60

    return Weekday.from_number(weekday_number), hour, minute


def get_current_minutes_since_week_started(tz: str = "UTC") -> int:
    """
    Get the current time in minutes since the start of the week.
    """
    now = datetime.now(pytz.timezone(tz))
    weekday = Weekday.from_number(now.weekday())

    return convert_time_data_to_minutes_since_week_started(weekday, now.hour, now.minute)
