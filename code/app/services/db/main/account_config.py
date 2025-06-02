from typing import Any, Dict, List, Optional

from db.database import MainSessionLocal
from models.main.account_config import AccountConfig
from quant_core.clients.mt5.mt5_client import Mt5Client
from quant_core.enums.stagger_method import StaggerMethod
from quant_core.enums.trade_mode import TradeMode
from services.symbol_lookup import ALL_SYMBOLS


def get_all_configs() -> List[AccountConfig]:
    """Get all account configurations."""
    with MainSessionLocal() as session:
        return session.query(AccountConfig).all()


def get_configs_by_account_id(account_id: str) -> List[AccountConfig]:
    """Get all configurations for a given account ID."""
    with MainSessionLocal() as session:
        return session.query(AccountConfig).filter_by(account_id=account_id).all()


def get_config_by_account_and_symbol(account_id: str, signal_asset_id: str) -> Optional[AccountConfig]:
    """Get a configuration for a given account ID and signal asset ID."""
    with MainSessionLocal() as session:
        return session.query(AccountConfig).filter_by(account_id=account_id, signal_asset_id=signal_asset_id).first()


def upsert_config(account_id: str, config: Dict[str, Any]) -> None:
    """Insert or update a configuration for a given account ID."""
    with MainSessionLocal() as session:
        existing = (
            session.query(AccountConfig)
            .filter_by(account_id=account_id, signal_asset_id=config["signal_asset_id"])
            .first()
        )

        if existing:
            for k, v in config.items():
                setattr(existing, k, v)
        else:
            new_config = AccountConfig(account_id=account_id, **config)
            session.add(new_config)

        session.commit()


def upsert_multiple_configs(account_id: str, configs: List[Dict[str, Any]]):
    """Insert or update multiple configurations for a given account ID."""
    with MainSessionLocal() as session:
        for config in configs:
            if not config.get("signal_asset_id") or not config.get("platform_asset_id"):
                continue

            existing = (
                session.query(AccountConfig)
                .filter_by(account_id=account_id, signal_asset_id=config["signal_asset_id"])
                .first()
            )

            if existing:
                for k, v in config.items():
                    setattr(existing, k, v)
            else:
                new_config = AccountConfig(account_id=account_id, **config)
                session.add(new_config)

        session.commit()


def delete_config(account_id: str, signal_asset_id: str) -> None:
    """Delete a configuration for a given account ID and signal asset ID."""
    with MainSessionLocal() as session:
        session.query(AccountConfig).filter_by(account_id=account_id, signal_asset_id=signal_asset_id).delete()
        session.commit()


def delete_all_configs(account_id: str) -> None:
    """Delete all configurations for a given account ID."""
    with MainSessionLocal() as session:
        session.query(AccountConfig).filter_by(account_id=account_id).delete()
        session.commit()


def sync_with_mt5(account_id: str, secret_id: str) -> None:
    """Sync account configurations with MT5 symbols."""
    client = Mt5Client(secret_id=secret_id)
    symbols = client.get_all_symbols()

    for symbol in symbols:
        upsert_config(
            account_id,
            {
                "signal_asset_id": symbol.name,
                "platform_asset_id": symbol.name,
                "entry_stagger_method": StaggerMethod.FIBONACCI.value,
                "n_staggers": 3,
                "risk_percent": 0.5,
                "decimal_points": symbol.digits,
                "lot_size": symbol.trade_contract_size,
                "enabled": False,
                "asset_type": ALL_SYMBOLS.get(symbol.name, None),
                "mode": TradeMode.DEFAULT.name,
            },
        )
