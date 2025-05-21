from typing import Optional, Set

import pandas as pd
from sqlalchemy import text

from db.database import CacheSessionLocal
from models.cache.balance_over_time import BalanceOverTimeCache
from models.cache.trade_history import Trade
from quant_core.clients.mt5.mt5_client import Mt5Client
from quant_core.enums.asset_type import AssetType
from quant_core.services.core_logger import CoreLogger
from services.db.main.account import get_all_accounts
from services.db.main.account_config import get_all_configs


def store_balance_over_time_cache(session: CacheSessionLocal, df: pd.DataFrame):
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
