from typing import List, Optional

from db.database import MainSessionLocal
from models.main.account import Account
from models.main.confluence_config import ConfluenceConfig
from quant_core.enums.confluences import Confluence
from quant_core.enums.trade_direction import EnabledTradeDirection
from quant_core.services.core_logger import CoreLogger
from sqlalchemy.orm import joinedload


class ConfluenceConfigService:
    """Service class for managing confluence configurations in the database."""

    @staticmethod
    def get_all_configs() -> List[ConfluenceConfig]:
        """Fetch all confluence configurations with their linked accounts."""
        with MainSessionLocal() as session:
            CoreLogger().debug("Fetching all confluence configs with account relation.")
            return session.query(ConfluenceConfig).options(joinedload(ConfluenceConfig.account)).all()

    @staticmethod
    def get_configs_by_account(account_uid: str) -> List[ConfluenceConfig]:
        """Fetch all confluences for a given account using the relationship."""
        with MainSessionLocal() as session:
            account = (
                session.query(Account)
                .options(joinedload(Account.confluence_configs))
                .filter_by(uid=account_uid)
                .first()
            )
            if account:
                return account.confluence_configs
            CoreLogger().warning(f"No account found for UID: {account_uid}")
            return []

    @staticmethod
    def get_config(account_uid: str, confluence_id: str) -> Optional[ConfluenceConfig]:
        """Fetch a single confluence config using composite PK."""
        with MainSessionLocal() as session:
            return (
                session.query(ConfluenceConfig)
                .filter_by(account_id=account_uid, confluence_id=confluence_id)
                .options(joinedload(ConfluenceConfig.account))
                .first()
            )

    @staticmethod
    def upsert_config(
        account_uid: str,
        confluence_id: str,
        min_value: float = 0.9,
        max_value: float = 1.1,
        enabled_trade_direction: EnabledTradeDirection = EnabledTradeDirection.BOTH,
    ) -> None:
        """Insert or update a single confluence config."""
        with MainSessionLocal() as session:
            account = (
                session.query(Account)
                .options(joinedload(Account.confluence_configs))
                .filter_by(uid=account_uid)
                .first()
            )
            if not account:
                CoreLogger().warning(f"Cannot upsert config: Account with UID {account_uid} not found.")
                return

            existing = {cfg.confluence_id: cfg for cfg in account.confluence_configs}

            if confluence_id in existing:
                cfg = existing[confluence_id]
                CoreLogger().debug(f"Updating existing confluence {confluence_id} for account {account_uid}")
                cfg.min_value = min_value
                cfg.max_value = max_value
                cfg.enabled_trade_direction = enabled_trade_direction
            else:
                CoreLogger().debug(f"Adding new confluence {confluence_id} for account {account_uid}")
                new_cfg = ConfluenceConfig(
                    account_id=account_uid,
                    confluence_id=confluence_id,
                    min_value=min_value,
                    max_value=max_value,
                    enabled_trade_direction=enabled_trade_direction,
                )
                account.confluence_configs.append(new_cfg)

            session.commit()
            CoreLogger().info(f"Upserted confluence {confluence_id} for account {account_uid}")

    @staticmethod
    def delete_config(account_uid: str, confluence_id: str) -> None:
        """Delete a specific confluence configuration."""
        with MainSessionLocal() as session:
            con = session.query(ConfluenceConfig).filter_by(account_id=account_uid, confluence_id=confluence_id).first()
            if con:
                session.delete(con)
                session.commit()
                CoreLogger().info(f"Deleted confluence {confluence_id} for account {account_uid}")
            else:
                CoreLogger().warning(f"No confluence found for deletion: {confluence_id} + {account_uid}")

    @staticmethod
    def delete_all_configs_for_account(account_uid: str) -> None:
        """Delete all confluences for an account using the relationship."""
        with MainSessionLocal() as session:
            account = (
                session.query(Account)
                .options(joinedload(Account.confluence_configs))
                .filter_by(uid=account_uid)
                .first()
            )
            if account:
                CoreLogger().info(f"Clearing all confluences for account {account_uid}")
                account.confluence_configs.clear()
                session.commit()
            else:
                CoreLogger().warning(f"No account found for UID {account_uid}")

    @staticmethod
    def toggle_confluence(account_uid: str, confluence_id: str) -> Optional[ConfluenceConfig]:
        """Toggle a confluence between DISABLED and BOTH."""
        with MainSessionLocal() as session:
            con = session.query(ConfluenceConfig).filter_by(account_id=account_uid, confluence_id=confluence_id).first()
            if con:
                new_state = (
                    EnabledTradeDirection.DISABLED
                    if con.enabled_trade_direction != EnabledTradeDirection.DISABLED
                    else EnabledTradeDirection.BOTH
                )
                con.enabled_trade_direction = new_state
                session.commit()
                CoreLogger().info(f"Toggled confluence {confluence_id} for account {account_uid} to {new_state.name}")
                return con
            CoreLogger().warning(f"Confluence not found for toggle: {confluence_id} + {account_uid}")
            return None

    @staticmethod
    def sync_confluences(account_uid: str) -> None:
        """Ensure all code-defined confluences are present for a given account."""
        with MainSessionLocal() as session:
            account = (
                session.query(Account)
                .options(joinedload(Account.confluence_configs))
                .filter_by(uid=account_uid)
                .first()
            )

            if not account:
                CoreLogger().warning(f"Cannot sync confluences: Account '{account_uid}' not found.")
                return

            existing_ids = {cfg.confluence_id for cfg in account.confluence_configs}
            new_confluences = []

            for confluence in list(Confluence):
                if confluence.name not in existing_ids:
                    CoreLogger().info(f"Adding missing confluence '{confluence.name}' to account '{account_uid}'")
                    cfg = ConfluenceConfig(
                        account_id=account_uid,
                        confluence_id=confluence.name,
                        min_value=0.9,
                        max_value=1.1,
                        enabled_trade_direction=EnabledTradeDirection.BOTH,
                    )
                    new_confluences.append(cfg)

            account.confluence_configs.extend(new_confluences)
            session.commit()
