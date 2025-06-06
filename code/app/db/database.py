import os

from models.cache.balance_over_time import BalanceOverTimeCache
from models.cache.trade_history import Trade
from models.main.account import Account
from models.main.account_config import AccountConfig
from models.main.confluence import ConfluenceConfig
from models.main.general_setting import GeneralSetting
from models.main.grid_bot import GridBot
from quant_core.services.core_logger import CoreLogger
from sqlalchemy import create_engine, inspect
from sqlalchemy.orm import sessionmaker

MAIN_DATABASE_PATH = os.path.join(os.path.dirname(__file__), "data", "database.db")
if not os.path.exists(os.path.dirname(MAIN_DATABASE_PATH)):
    os.makedirs(os.path.dirname(MAIN_DATABASE_PATH))

CACHE_DATABASE_PATH = os.path.join(os.path.dirname(__file__), "data", "cache.db")
if not os.path.exists(os.path.dirname(CACHE_DATABASE_PATH)):
    os.makedirs(os.path.dirname(CACHE_DATABASE_PATH))

MAIN_DATABASE_URL = f"sqlite:///{MAIN_DATABASE_PATH}"
CACHE_DATABASE_URL = f"sqlite:///{CACHE_DATABASE_PATH}"

MAIN_TABLES = [
    ("main_accounts", Account),
    ("main_confluences", ConfluenceConfig),
    ("main_general_settings", GeneralSetting),
    ("main_account_configs", AccountConfig),
    ("main_grid_bots", GridBot),
]
CACHE_TABLES = [("cache_trade_history", Trade), ("cache_balance_over_time", BalanceOverTimeCache)]

main_engine = create_engine(MAIN_DATABASE_URL, echo=False)
MainSessionLocal = sessionmaker(bind=main_engine)

cache_engine = create_engine(CACHE_DATABASE_URL, echo=False)
CacheSessionLocal = sessionmaker(bind=cache_engine)


def init_db() -> None:
    """Initialize the database on first run."""
    main_inspector = inspect(main_engine)
    main_tables = main_inspector.get_table_names()

    cache_inspector = inspect(cache_engine)
    cache_tables = cache_inspector.get_table_names()

    CoreLogger().debug(f"Current Main DB Tables: {main_tables}")
    CoreLogger().debug(f"Current Cache DB Tables: {cache_tables}")

    for table_name, model in MAIN_TABLES:
        if table_name not in main_tables:
            CoreLogger().debug(f"Creating table: {table_name}")
            model.metadata.create_all(bind=main_engine)
        else:
            CoreLogger().debug(f"Table already exists: {table_name}")

    for table_name, model in CACHE_TABLES:
        if table_name not in cache_tables:
            CoreLogger().debug(f"Creating table: {table_name}")
            model.metadata.create_all(bind=cache_engine)
        else:
            CoreLogger().debug(f"Table already exists: {table_name}")

    CoreLogger().info("✅ Database initialization complete.")
