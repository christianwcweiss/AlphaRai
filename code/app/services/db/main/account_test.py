from unittest.mock import patch

from models.main.account import Account
from quant_core.enums.platform import Platform
from quant_core.enums.prop_firm import PropFirm
from quant_dev.builder import Builder
from services.db.main.account import AccountService


class TestAccountService:
    def test_get_all_accounts_returns_accounts(self):
        with Builder.temporary_test_db(Account) as test_session_local:
            with patch("services.db.main.account.MainSessionLocal", test_session_local):
                service = AccountService()
                uid = Builder.build_random_string()
                service.upsert_account(
                    friendly_name=Builder.build_random_string(),
                    secret_name=Builder.build_random_string(),
                    platform=Builder.get_random_item(list(Platform)),
                    prop_firm=Builder.get_random_item(list(PropFirm)),
                    uid=uid,
                )

                accounts = service.get_all_accounts()

                assert len(accounts) == 1
                assert accounts[0].uid == uid

    def test_get_account_by_uid_found(self):
        with Builder.temporary_test_db(Account) as test_session_local:
            with patch("services.db.main.account.MainSessionLocal", test_session_local):
                service = AccountService()
                uid = Builder.build_random_string()
                service.upsert_account(
                    friendly_name=Builder.build_random_string(),
                    secret_name=Builder.build_random_string(),
                    platform=Builder.get_random_item(list(Platform)),
                    prop_firm=Builder.get_random_item(list(PropFirm)),
                    uid=uid,
                )

                result = service.get_account_by_uid(uid)

                assert result is not None
                assert result.uid == uid

    def test_get_accounts_with_filters(self):
        with Builder.temporary_test_db(Account) as test_session_local:
            with patch("services.db.main.account.MainSessionLocal", test_session_local):
                service = AccountService()
                platform = Builder.get_random_item(list(Platform))
                prop_firm = Builder.get_random_item(list(PropFirm))

                uid1 = Builder.build_random_string()
                uid2 = Builder.build_random_string()

                service.upsert_account(
                    friendly_name=Builder.build_random_string(),
                    secret_name=Builder.build_random_string(),
                    platform=platform,
                    prop_firm=prop_firm,
                    uid=uid1,
                )
                service.upsert_account(
                    friendly_name=Builder.build_random_string(),
                    secret_name=Builder.build_random_string(),
                    platform=platform,
                    prop_firm=prop_firm,
                    uid=uid2,
                )
                service.toggle_account_enabled(uid2)

                results = service.get_accounts_with_filter(platform=platform, prop_firm=prop_firm, enabled=True)

                assert len(results) == 1
                assert results[0].uid == uid2

    def test_delete_account_removes_existing(self):
        with Builder.temporary_test_db(Account) as test_session_local:
            with patch("services.db.main.account.MainSessionLocal", test_session_local):
                service = AccountService()
                uid = Builder.build_random_string()
                service.upsert_account(
                    friendly_name=Builder.build_random_string(),
                    secret_name=Builder.build_random_string(),
                    platform=Builder.get_random_item(list(Platform)),
                    prop_firm=Builder.get_random_item(list(PropFirm)),
                    uid=uid,
                )

                service.delete_account(uid)

                assert service.get_account_by_uid(uid) is None

    def test_toggle_account_enabled_switches_flag(self):
        with Builder.temporary_test_db(Account) as test_session_local:
            with patch("services.db.main.account.MainSessionLocal", test_session_local):
                service = AccountService()
                uid = Builder.build_random_string()
                service.upsert_account(
                    friendly_name=Builder.build_random_string(),
                    secret_name=Builder.build_random_string(),
                    platform=Builder.get_random_item(list(Platform)),
                    prop_firm=Builder.get_random_item(list(PropFirm)),
                    uid=uid,
                )

                account = service.get_account_by_uid(uid)

                assert account.enabled is False

                service.toggle_account_enabled(account.uid)
                account = service.get_account_by_uid(account.uid)

                assert account.enabled is True
