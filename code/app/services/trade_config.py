from db.database import SessionLocal
from models.trade_config import TradeConfig

def get_configs_by_uid(uid: str) -> list[TradeConfig]:
    with SessionLocal() as session:
        return session.query(TradeConfig).filter_by(uid=uid).all()

def upsert_config(uid: str, config: dict):
    with SessionLocal() as session:
        obj = session.query(TradeConfig).filter_by(uid=uid, signal_asset_id=config["signal_asset_id"]).first()
        if obj:
            for k, v in config.items():
                setattr(obj, k, v)
        else:
            obj = TradeConfig(uid=uid, **config)
            session.add(obj)
        session.commit()

def delete_config(uid: str, signal_asset_id: str):
    with SessionLocal() as session:
        session.query(TradeConfig).filter_by(uid=uid, signal_asset_id=signal_asset_id).delete()
        session.commit()