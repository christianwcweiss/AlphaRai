from datetime import datetime, timedelta, UTC

import pytz


def get_tomorrow_formatted() -> str:
    tomorrow = datetime.now(UTC) + timedelta(days=1)

    return tomorrow.strftime("%d-%b-%y").upper()


from croniter import croniter
from datetime import datetime
import humanize


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
    try:
        now = datetime.now(pytz.timezone(tz))
        itr = croniter(cron, now)
        next_time = itr.get_next(datetime)
        delta = next_time - now

        seconds = int(delta.total_seconds())
        if seconds < 0:
            return f"⚠️ Cron is valid but next run was in the past ({next_time})"
        elif seconds < 60:
            return f"⏱️ Next run in {seconds} sec (at {next_time.strftime('%Y-%m-%d %H:%M')})"
        elif seconds < 3600:
            return f"⏱️ Next run in {seconds//60} min (at {next_time.strftime('%Y-%m-%d %H:%M')})"
        else:
            return f"📅 Next run at {next_time.strftime('%Y-%m-%d %H:%M')}"

    except Exception as e:
        return f"❌ Invalid cron: {e}"
