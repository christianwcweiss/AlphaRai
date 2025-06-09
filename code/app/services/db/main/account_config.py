from typing import Any, Dict, List, Optional, Union

from sqlalchemy.orm import joinedload

from db.database import MainSessionLocal
from models.main.account import Account
from models.main.account_config import AccountConfig
from quant_core.clients.mt5.mt5_client import Mt5Client
from quant_core.enums.stagger_method import StaggerMethod
from quant_core.enums.trade_mode import TradeMode
from quant_core.services.core_logger import CoreLogger
from services.symbol_lookup import ALL_SYMBOLS


class AccountConfigService:
    """Service class for managing account configurations in the database."""

    @staticmethod
    def get_all_configs() -> List[AccountConfig]:
        """Fetch all account configurations with their linked accounts."""
        with MainSessionLocal() as session:
            CoreLogger().debug("Fetching all account configs with account relation.")
            return session.query(AccountConfig).options(joinedload(AccountConfig.account)).all()

    @staticmethod
    def get_configs_by_account(account_uid: str) -> List[AccountConfig]:
        """Fetch all configurations for a given account using the relationship."""
        with MainSessionLocal() as session:
            account = session.query(Account).options(joinedload(Account.account_configs)).filter_by(uid=account_uid).first()
            if account:
                return account.account_configs
            CoreLogger().warning(f"No account found for UID: {account_uid}")
            return []

    @staticmethod
    def get_config(account_uid: str, platform_asset_id: str) -> Optional[AccountConfig]:
        """Fetch a single config using composite PK."""
        with MainSessionLocal() as session:
            return (
                session.query(AccountConfig)
                .filter_by(account_id=account_uid, platform_asset_id=platform_asset_id)
                .options(joinedload(AccountConfig.account))
                .first()
            )

    @staticmethod
    def upsert_configs(account_uid: str, configs: Union[Dict[str, Any], List[Dict[str, Any]]]) -> None:
        """Insert or update one or multiple configurations for a given account using relationships."""
        if isinstance(configs, dict):
            configs = [configs]

        with MainSessionLocal() as session:
            account = session.query(Account).options(joinedload(Account.account_configs)).filter_by(uid=account_uid).first()
            if not account:
                CoreLogger().warning(f"Cannot upsert configs: Account with UID {account_uid} not found.")
                return

            existing_configs = {cfg.platform_asset_id: cfg for cfg in account.account_configs}

            for config in configs:
                platform_asset_id = config.get("platform_asset_id")
                signal_asset_id = config.get("signal_asset_id")
                if not platform_asset_id or not signal_asset_id:
                    CoreLogger().warning(f"Skipping config: missing platform_asset_id or signal_asset_id: {config}")
                    continue

                if platform_asset_id in existing_configs:
                    cfg = existing_configs[platform_asset_id]
                    CoreLogger().debug(f"Updating existing config for {account_uid} - {platform_asset_id}")
                    for k, v in config.items():
                        setattr(cfg, k, v)
                else:
                    CoreLogger().debug(f"Adding new config for {account_uid} - {platform_asset_id}")
                    new_config = AccountConfig(account_id=account_uid, **config)
                    account.account_configs.append(new_config)

            session.commit()
            CoreLogger().info(f"Finished upserting configs for account {account_uid}")

    @staticmethod
    def delete_config(account_uid: str, platform_asset_id: str) -> None:
        """Delete a specific configuration."""
        with MainSessionLocal() as session:
            config = (
                session.query(AccountConfig)
                .filter_by(account_id=account_uid, platform_asset_id=platform_asset_id)
                .first()
            )
            if config:
                session.delete(config)
                session.commit()
                CoreLogger().info(f"Deleted config for {account_uid} + {platform_asset_id}")
            else:
                CoreLogger().warning(f"No config found for deletion: {account_uid} + {platform_asset_id}")

    @staticmethod
    def delete_all_configs_for_account(account_uid: str) -> None:
        """Delete all configs using the relationship."""
        with MainSessionLocal() as session:
            account = session.query(Account).options(joinedload(Account.account_configs)).filter_by(uid=account_uid).first()
            if account:
                CoreLogger().info(f"Clearing all configs for account {account_uid}")
                account.account_configs.clear()
                session.commit()
            else:
                CoreLogger().warning(f"No account found for UID {account_uid}")

    @staticmethod
    def sync_with_mt5(account_uid: str, secret_id: str) -> None:
        """Sync account configs from MT5 using the relationship."""
        CoreLogger().info(f"Syncing MT5 symbols for account {account_uid}")
        symbols = Mt5Client(secret_id=secret_id).get_all_symbols()

        configs = [
            {
                "signal_asset_id": symbol.name,
                "platform_asset_id": symbol.name,
                "entry_stagger_method": StaggerMethod.FIBONACCI.value,
                "n_staggers": 3,
                "risk_percent": 0.5,
                "decimal_points": symbol.digits,
                "lot_size": symbol.trade_contract_size,
                "enabled": False,
                "asset_type": ALL_SYMBOLS.get(symbol.name),
                "mode": TradeMode.DEFAULT.name,
            }
            for symbol in symbols
        ]

        AccountConfigService.upsert_configs(account_uid, configs)
