from datetime import timedelta, UTC

import pytz
from croniter import croniter
from datetime import datetime


def get_tomorrow_formatted() -> str:
    """Get tomorrow's date formatted as 'DD-MMM-YY' in uppercase."""
    tomorrow = datetime.now(UTC) + timedelta(days=1)

    return tomorrow.strftime("%d-%b-%y").upper()


def is_valid_cron(cron_expr: str) -> bool:
    """
    Returns True if the cron expression is valid, False otherwise.
    """
    try:
        croniter(cron_expr, datetime.now())
        return True
    except (ValueError, KeyError):
        return False


def describe_cron(cron: str, tz="UTC") -> str:
    """Describe the next run time of a cron expression."""
    try:
        now = datetime.now(pytz.timezone(tz))
        itr = croniter(cron, now)
        next_time = itr.get_next(datetime)
        delta = next_time - now

        seconds = int(delta.total_seconds())
        if seconds < 0:
            return f"Cron is valid but next run was in the past ({next_time})"
        if seconds < 60:
            return f"Next run in {seconds} sec (at {next_time.strftime('%Y-%m-%d %H:%M')})"
        if seconds < 3600:
            return f"Next run in {seconds//60} min (at {next_time.strftime('%Y-%m-%d %H:%M')})"

        return f"Next run at {next_time.strftime('%Y-%m-%d %H:%M')}"

    except Exception as error:  # pylint: disable=broad-exception-caught
        return f"Invalid cron: {error}"
