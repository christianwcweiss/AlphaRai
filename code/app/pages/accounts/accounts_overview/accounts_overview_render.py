import pandas as pd
from dash import html

from components.atoms.layout.layout import AlphaCol, AlphaRow
from components.molecules.cards.accounts.account_card import AccountCard
from models.main.account import Account
from quant_core.metrics.account_balance_over_time.balance_over_time import AccountBalanceOverTime
from services.db.cache.trade_history import get_all_trades_df
from services.db.main.account import AccountService


def _render_account_card(account: Account, history_data_frame: pd.DataFrame) -> html.Div:
    """Render the account card with the given account and relative DataFrame."""
    data_frame = (
        history_data_frame[history_data_frame["account_id"] == account.uid] if not history_data_frame.empty else None
    )

    return AccountCard(account, data_frame).render()


def render_all_accounts():
    """Reload the MT5 accounts and their trades."""
    accounts = sorted(AccountService.get_all_accounts(), key=lambda x: x.friendly_name)
    trades_df = get_all_trades_df()

    balance_df = AccountBalanceOverTime().calculate(
        data_frame=trades_df,
    )

    return AlphaRow(
        [AlphaCol(_render_account_card(account, balance_df), xs=12, sm=6, md=4, lg=3, xl=3) for account in accounts]
    )
