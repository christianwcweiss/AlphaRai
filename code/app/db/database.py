import os

from sqlalchemy import create_engine, inspect
from sqlalchemy.orm import sessionmaker

from models.account import Account
from models.account_config import AccountConfig
from models.confluence import ConfluenceConfig
from models.general_setting import GeneralSetting
from models.trade_history import Trade
from quant_core.services.core_logger import CoreLogger

DATABASE_PATH = os.path.join(os.path.dirname(__file__), "data", "database.db")
if not os.path.exists(os.path.dirname(DATABASE_PATH)):
    os.makedirs(os.path.dirname(DATABASE_PATH))

DATABASE_URL = f"sqlite:///{DATABASE_PATH}"
TABLES = [
    ("accounts", Account),
    ("confluences", ConfluenceConfig),
    ("general_settings", GeneralSetting),
    ("trade_config", AccountConfig),
    ("trades", Trade),
]

engine = create_engine(DATABASE_URL, echo=False)
SessionLocal = sessionmaker(bind=engine)


def init_db() -> None:
    inspector = inspect(engine)
    tables = inspector.get_table_names()

    CoreLogger().debug(f"Current DB Tables: {tables}")

    for table_name, model in TABLES:
        if table_name not in tables:
            CoreLogger().debug(f"Creating table: {table_name}")
            model.metadata.create_all(bind=engine)
        else:
            CoreLogger().debug(f"Table already exists: {table_name}")

    CoreLogger().info("✅ Database initialization complete.")
