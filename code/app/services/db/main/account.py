from typing import List, Optional

from db.database import MainSessionLocal
from models.main.account import Account
from quant_core.enums.platform import Platform
from quant_core.enums.prop_firm import PropFirm
from quant_core.services.core_logger import CoreLogger
from quant_core.utils.text_utils import generate_uid


class AccountService:
    """Service class for managing accounts in the database."""

    @staticmethod
    def get_all_accounts() -> List[Account]:
        """Fetch all accounts from the database."""
        with MainSessionLocal() as session:
            CoreLogger().debug("Fetching all accounts from the database.")
            return session.query(Account).all()

    @staticmethod
    def get_account_by_uid(uid: str) -> Optional[Account]:
        """Fetch a single account by UID."""
        with MainSessionLocal() as session:
            CoreLogger().debug(f"Fetching account with uid: {uid}")
            return session.query(Account).filter_by(uid=uid).first()

    @staticmethod
    def get_accounts_with_filter(
        platform: Optional[Platform] = None, prop_firm: Optional[PropFirm] = None, enabled: Optional[bool] = None
    ) -> List[Account]:
        """Fetch accounts with optional filters."""
        with MainSessionLocal() as session:
            query = session.query(Account)
            if platform:
                query = query.filter_by(platform=platform)
            if prop_firm:
                query = query.filter_by(prop_firm=prop_firm)
            if enabled is not None:
                query = query.filter_by(enabled=enabled)

            return query.all()

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
    def delete_account(uid: str) -> None:
        """Delete an account by UID."""
        with MainSessionLocal() as session:
            account = session.query(Account).filter_by(uid=uid).first()
            if account:
                session.delete(account)
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


def get_all_accounts() -> List[Account]:
    """Fetch all credential settings from the database."""
    with MainSessionLocal() as session:
        CoreLogger().debug("Fetching all accounts from the database.")
        return session.query(Account).all()


def get_account_by_uid(uid: str) -> Optional[Account]:
    """Fetch a single account by UID."""
    with MainSessionLocal() as session:
        CoreLogger().debug(f"Fetching account with uid: {uid}")
        return session.query(Account).filter_by(uid=uid).first()


def upsert_account(platform: str, friendly_name: str, secret_name: str, uid: str) -> Account:
    """Upsert an account in the database."""
    with MainSessionLocal() as session:
        CoreLogger().info(
            f"Upserting credential settings for platform: "
            f"{platform}, uid: {uid}, friendly_name: {friendly_name}, secret_name: {secret_name}"
        )
        account = session.query(Account).filter_by(platform=platform, uid=uid).first()

        if account:
            account.friendly_name = friendly_name
            account.secret_name = secret_name
        else:
            account = Account(uid=uid, platform=platform, friendly_name=friendly_name, secret_name=secret_name)
            session.add(account)

        session.commit()

        return account


def delete_account(platform: str, uid: str) -> None:
    """Delete an account by platform and UID."""
    with MainSessionLocal() as session:
        account = session.query(Account).filter_by(platform=platform, uid=uid).first()
        if account:
            session.delete(account)
            session.commit()
            CoreLogger().info(f"Deleted account {uid}")
        else:
            CoreLogger().warning(f"No account found for UID: {uid}")


def toggle_account_enabled(uid: str) -> Account:
    """Toggle the enabled status of an account."""
    with MainSessionLocal() as session:
        account = session.query(Account).filter_by(uid=uid).first()
        if account:
            account.enabled = not account.enabled
            CoreLogger().info(f"Toggled account {uid} to {'ENABLED' if account.enabled else 'DISABLED'}.")
            session.commit()

        return account
