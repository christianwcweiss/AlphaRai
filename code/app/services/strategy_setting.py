from db.database import SessionLocal
from models.strategy_setting import StrategySetting
from quant_core.services.core_logger import CoreLogger


def get_settings_for_strategy(strategy_id: str) -> list[StrategySetting]:
    with SessionLocal() as session:
        return session.query(StrategySetting).filter_by(strategy_id=strategy_id).all()


def add_strategy_setting(
    strategy_id: str, strategy_hash: str, account: str, asset: str, cron_expr: str = None, enabled: bool = False
):
    with SessionLocal() as session:
        setting = StrategySetting(
            strategy_id=strategy_id,
            strategy_hash=strategy_hash,
            account=account,
            asset=asset,
            cron_expression=cron_expr,
            enabled=enabled,
        )
        session.add(setting)
        session.commit()
        CoreLogger().info(f"✅ Added setting for {strategy_id}: {account} / {asset}")


def delete_strategy_setting(setting_id: int):
    with SessionLocal() as session:
        deleted = session.query(StrategySetting).filter_by(id=setting_id).delete()
        session.commit()
        CoreLogger().info(f"🗑️ Deleted strategy setting {setting_id} ({deleted} row)")
