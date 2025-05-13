from datetime import timedelta, UTC

from datetime import datetime
from typing import Union

import pytz
from croniter import croniter


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
