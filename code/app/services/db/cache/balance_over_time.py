import pandas as pd

from db.database import CacheSessionLocal
from models.cache.balance_over_time import BalanceOverTimeCache


def store_balance_over_time_cache(session: CacheSessionLocal, df: pd.DataFrame):
    """Store balance over time cache in the database."""
    records = [
        BalanceOverTimeCache(
            account_id=row.get("account_id"),
            symbol=row.get("symbol"),
            asset_type=row.get("asset_type"),
            hour=row.get("hour"),
            weekday=row.get("weekday"),
            closed_at=row["closed_at"],
            initial_balance=row["initial_balance"],
            absolute_balance=row["absolute_balance"],
            initial_balance_pct=row["initial_balance_pct"],
            relative_balance=row["relative_balance"],
        )
        for _, row in df.iterrows()
        if row["absolute_balance"]
    ]
    session.bulk_save_objects(records)
    session.commit()
