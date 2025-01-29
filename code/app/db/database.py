import os

from sqlalchemy import create_engine, inspect
from sqlalchemy.orm import sessionmaker

from models.credential_setting import CredentialSetting
from models.strategy import Strategy
from models.strategy_setting import StrategySetting
from models.trade_config import TradeConfig
from quant_core.services.core_logger import CoreLogger

DATABASE_PATH = os.path.join(os.path.dirname(__file__), "data", "database.db")
if not os.path.exists(os.path.dirname(DATABASE_PATH)):
    os.makedirs(os.path.dirname(DATABASE_PATH))

DATABASE_URL = f"sqlite:///{DATABASE_PATH}"
TABLES = [
    "credential_settings",
    "trade_config",
    "strategy_settings",
    "strategies"
]

engine = create_engine(DATABASE_URL, echo=False)
SessionLocal = sessionmaker(bind=engine)


def init_db():
    inspector = inspect(engine)
    tables = inspector.get_table_names()

    CoreLogger().debug(f"🧠 Current DB Tables: {tables}")

    # Create strategy-related tables if missing
    if "strategies" not in tables:
        CoreLogger().info("Creating table: strategies")
        Strategy.__table__.create(engine)

    if "strategy_settings" not in tables:
        CoreLogger().info("Creating table: strategy_settings")
        StrategySetting.__table__.create(engine)

    if "credential_settings" not in tables:
        CoreLogger().info("Creating table: credential_settings")
        CredentialSetting.__table__.create(engine)

    if "trade_config" not in tables:
        CoreLogger().info("Creating table: trade_config")
        TradeConfig.__table__.create(engine)

    CoreLogger().info("✅ Database initialization complete (no tables dropped)")

