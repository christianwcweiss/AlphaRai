from typing import List, Optional

from db.database import MainSessionLocal
from models.main.account import Account
from models.main.account_config import AccountConfig
from quant_core.enums.platform import Platform
from quant_core.enums.prop_firm import PropFirm
from quant_core.services.core_logger import CoreLogger
from quant_core.utils.text_utils import generate_uid
from sqlalchemy.orm import joinedload


class AccountService:
    """Service class for managing accounts in the database."""

    @staticmethod
    def get_all_accounts() -> List[Account]:
        """Fetch all accounts from the database, including their configs."""
        with MainSessionLocal() as session:
            CoreLogger().debug("Fetching all accounts with configs from the database.")
            return session.query(Account).options(joinedload(Account.account_configs)).all()

    @staticmethod
    def get_account_by_uid(uid: str) -> Optional[Account]:
        """Fetch a single account by UID with its configs."""
        with MainSessionLocal() as session:
            CoreLogger().debug(f"Fetching account with uid: {uid}")
            return session.query(Account).options(joinedload(Account.account_configs)).filter_by(uid=uid).first()

    @staticmethod
    def get_accounts_with_filter(
        platform: Optional[Platform] = None, prop_firm: Optional[PropFirm] = None, enabled: Optional[bool] = None
    ) -> List[Account]:
        """Fetch accounts with optional filters."""
        with MainSessionLocal() as session:
            query = session.query(Account).options(joinedload(Account.account_configs))
            if platform:
                query = query.filter_by(platform=platform)
            if prop_firm:
                query = query.filter_by(prop_firm=prop_firm)
            if enabled is not None:
                query = query.filter_by(enabled=enabled)

            return query.all()

    @staticmethod
    def get_account_configs(uid: str) -> Optional[List[AccountConfig]]:
        """Fetch all configs for a given account UID."""
        with MainSessionLocal() as session:
            CoreLogger().debug(f"Fetching configs for account uid: {uid}")
            account = session.query(Account).options(joinedload(Account.account_configs)).filter_by(uid=uid).first()
            if account:
                return account.account_configs
            CoreLogger().warning(f"No account found for UID: {uid}")
            return None

    @staticmethod
    def upsert_account(
        friendly_name: str,
        secret_name: str,
        platform: Platform,
        prop_firm: PropFirm,
        uid: Optional[str] = None,
    ) -> Account:
        """Upsert an account in the database."""
        with MainSessionLocal() as session:
            if uid is None:
                uid = generate_uid()
                CoreLogger().info(f"Generated new UID for account: {uid}")

            account = session.query(Account).filter_by(uid=uid).first()
            if account is None:
                CoreLogger().info(f"Creating new account with uid: {uid}")
                account = Account(
                    uid=uid,
                    platform=platform,
                    prop_firm=prop_firm,
                    friendly_name=friendly_name,
                    secret_name=secret_name,
                )
                session.add(account)
            else:
                CoreLogger().info(f"Updating existing account with uid: {uid}")
                account.friendly_name = friendly_name
                account.secret_name = secret_name
                account.platform = platform
                account.prop_firm = prop_firm
            session.commit()

        return account

    @staticmethod
    def create_account_with_config(  # pylint: disable=too-many-arguments, too-many-positional-arguments
        friendly_name: str,
        secret_name: str,
        platform: Platform,
        prop_firm: PropFirm,
        config: dict,
        uid: Optional[str] = None,
    ) -> Account:
        """Create a new account and one initial AccountConfig."""
        with MainSessionLocal() as session:
            if uid is None:
                uid = generate_uid()
                CoreLogger().info(f"Generated new UID for account: {uid}")

            CoreLogger().info(f"Creating account with config: {uid}")
            account = Account(
                uid=uid,
                platform=platform,
                prop_firm=prop_firm,
                friendly_name=friendly_name,
                secret_name=secret_name,
            )
            account.account_configs.append(AccountConfig(**config, account_id=uid))
            session.add(account)
            session.commit()
            return account

    @staticmethod
    def delete_account(uid: str) -> None:
        """Delete an account and its configs by UID."""
        with MainSessionLocal() as session:
            account = session.query(Account).filter_by(uid=uid).first()
            if account:
                session.delete(account)  # Deletes related configs due to cascade
                session.commit()
                CoreLogger().info(f"Deleted account with uid: {uid}")
            else:
                CoreLogger().warning(f"No account found for UID: {uid}")

    @staticmethod
    def toggle_account_enabled(uid: str) -> Optional[Account]:
        """Toggle the enabled status of an account."""
        with MainSessionLocal() as session:
            account = session.query(Account).filter_by(uid=uid).first()
            if account:
                account.enabled = not account.enabled
                CoreLogger().info(f"Toggled account {uid} to {'ENABLED' if account.enabled else 'DISABLED'}.")
                session.commit()
                return account

            CoreLogger().warning(f"No account found for UID: {uid}")
            return None
