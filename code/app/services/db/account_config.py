from db.database import SessionLocal
from models.account_config import AccountConfig
from quant_core.clients.mt5.mt5_client import Mt5Client
from quant_core.enums.asset_type import AssetType
from quant_core.enums.stagger_method import StaggerMethod


def get_configs_by_account_id(account_id: str) -> list[AccountConfig]:
    with SessionLocal() as session:
        return session.query(AccountConfig).filter_by(account_id=account_id).all()


def get_config_by_account_and_symbol(account_id: str, signal_asset_id: str) -> AccountConfig | None:
    with SessionLocal() as session:
        return session.query(AccountConfig).filter_by(
            account_id=account_id,
            signal_asset_id=signal_asset_id
        ).first()


def upsert_config(account_id: str, config: dict):
    with SessionLocal() as session:
        existing = session.query(AccountConfig).filter_by(
            account_id=account_id,
            signal_asset_id=config["signal_asset_id"]
        ).first()

        if existing:
            for k, v in config.items():
                setattr(existing, k, v)
        else:
            new_config = AccountConfig(account_id=account_id, **config)
            session.add(new_config)

        session.commit()


def upsert_multiple_configs(account_id: str, configs: list[dict]):
    with SessionLocal() as session:
        for config in configs:
            if not config.get("signal_asset_id") or not config.get("platform_asset_id"):
                continue  # Skip incomplete configs

            existing = session.query(AccountConfig).filter_by(
                account_id=account_id,
                signal_asset_id=config["signal_asset_id"]
            ).first()

            if existing:
                for k, v in config.items():
                    setattr(existing, k, v)
            else:
                new_config = AccountConfig(account_id=account_id, **config)
                session.add(new_config)

        session.commit()


def delete_config(account_id: str, signal_asset_id: str):
    with SessionLocal() as session:
        session.query(AccountConfig).filter_by(
            account_id=account_id,
            signal_asset_id=signal_asset_id
        ).delete()
        session.commit()


def delete_all_configs(account_id: str):
    with SessionLocal() as session:
        session.query(AccountConfig).filter_by(account_id=account_id).delete()
        session.commit()


def sync_with_mt5(account_id: str, secret_id: str):
    client = Mt5Client(secret_id=secret_id)
    symbols = client.get_all_symbols()

    for symbol in symbols:
        upsert_config(account_id, {
            "signal_asset_id": symbol["name"],
            "platform_asset_id": symbol["name"],
            "entry_stagger_method": StaggerMethod.LINEAR.value,
            "n_staggers": 1,
            "risk_percent": 0.5,
            "decimal_points": symbol["digits"],
            "lot_size": symbol.get("lot_size", 1.0),  # new field with fallback
            "enabled": False,
            "asset_type": None,
        })