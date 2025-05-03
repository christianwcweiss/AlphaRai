from db.database import SessionLocal
from models.account_config import AccountConfig


def get_configs_by_uid(uid: str) -> list[AccountConfig]:
    with SessionLocal() as session:
        return session.query(AccountConfig).filter_by(uid=uid).all()


def upsert_config(uid: str, config: dict):
    if not config.get("signal_asset_id") or not config.get("platform_asset_id"):
        raise ValueError("signal_asset_id and platform_asset_id must be provided.")

    with SessionLocal() as session:
        existing = session.query(AccountConfig).filter_by(uid=uid, signal_asset_id=config["signal_asset_id"]).first()
        if existing:
            for k, v in config.items():
                setattr(existing, k, v)
        else:
            new_config = AccountConfig(uid=uid, **config)
            session.add(new_config)
        session.commit()


def delete_config(uid: str, signal_asset_id: str):
    with SessionLocal() as session:
        session.query(AccountConfig).filter_by(uid=uid, signal_asset_id=signal_asset_id).delete()
        session.commit()
