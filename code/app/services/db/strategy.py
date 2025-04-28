from db.database import SessionLocal
from models.strategy import Strategy
from models.strategy_setting import StrategySetting
from quant_core.services.core_logger import CoreLogger


def get_all_registered_strategy_ids() -> set[str]:
    with SessionLocal() as session:
        return {s.id for s in session.query(Strategy).all()}


def get_all_registered_strategy_hashes() -> dict:
    with SessionLocal() as session:
        strategies = session.query(Strategy).all()
        return {s.strategy_hash: s for s in strategies}


def register_strategy(strategy_dict: dict):
    with SessionLocal() as session:
        existing = session.query(Strategy).filter_by(id=strategy_dict["id"]).first()

        if existing:
            if existing.strategy_hash == strategy_dict["hash"]:
                CoreLogger().info(f"Strategy {strategy_dict['id']} already registered with current hash.")
                return
            CoreLogger().warning(f"Strategy {strategy_dict['id']} hash changed. Updating.")
            existing.strategy_hash = strategy_dict["hash"]
        else:
            CoreLogger().info(f"Registering new strategy: {strategy_dict['id']}")
            session.add(
                Strategy(
                    id=strategy_dict["id"],
                    strategy_hash=strategy_dict["hash"],
                    strategy_type=strategy_dict["type"],
                    friendly_name=strategy_dict["id"],
                )
            )

        session.commit()


def unregister_strategy(strategy_id: str):
    with SessionLocal() as session:
        deleted_settings = session.query(StrategySetting).filter_by(strategy_id=strategy_id).delete()
        session.query(Strategy).filter_by(id=strategy_id).delete()
        session.commit()
        CoreLogger().info(f"🗑️ Unregistered strategy {strategy_id}, removed {deleted_settings} settings.")


def clean_stale_strategy_settings(current_strategies: list[dict]):
    current_map = {s["id"]: s["hash"] for s in current_strategies}
    with SessionLocal() as session:
        all_settings = session.query(StrategySetting).all()
        for setting in all_settings:
            expected_hash = current_map.get(setting.strategy_id)
            if not expected_hash:
                CoreLogger().warning(f"⚠️ Strategy {setting.strategy_id} missing from disk")
            elif expected_hash != setting.strategy_hash:
                CoreLogger().warning(f"⚠️ Hash mismatch for {setting.strategy_id}")
                # ❌ REMOVE THIS LINE if you don’t want deregistration:
                # session.delete(setting)
        session.commit()
