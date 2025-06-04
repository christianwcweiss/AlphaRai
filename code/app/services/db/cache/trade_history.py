import pandas as pd
from db.database import CacheSessionLocal
from models.cache.trade_history import Trade
from quant_core.clients.mt5.mt5_client import Mt5Client
from quant_core.enums.asset_type import AssetType
from quant_core.services.core_logger import CoreLogger
from services.db.main.account import AccountService
from services.db.main.account_config import AccountConfigService
from sqlalchemy import text


def get_all_trades() -> list[Trade]:
    """Fetch all trades from the database."""
    with CacheSessionLocal() as session:
        CoreLogger().debug("Fetching all trades from the database.")

        return session.query(Trade).all()


def get_all_trades_df(enrich: bool = True) -> pd.DataFrame:
    """Fetch all trades as a DataFrame."""
    all_trades = get_all_trades()
    trades_df = pd.DataFrame([t.__dict__ for t in all_trades])
    trades_df = trades_df[[col for col in trades_df.columns if not col.startswith("_sa_")]]

    if enrich:
        accounts = AccountService().get_all_accounts()
        accounts_df = pd.DataFrame([a.__dict__ for a in accounts])
        accounts_df = accounts_df[[col for col in accounts_df.columns if not col.startswith("_sa_")]]

        trades_df = trades_df.merge(accounts_df, left_on="account_id", right_on="uid", how="left")
        trades_df.drop(columns=["id_x", "id_y", "enabled", "uid"], inplace=True)

        accounts_config = AccountConfigService().get_all_configs()
        accounts_config_df = pd.DataFrame([c.__dict__ for c in accounts_config])
        accounts_config_df = accounts_config_df[
            [col for col in accounts_config_df.columns if not col.startswith("_sa_")]
        ]
        accounts_config_df["asset_type"] = accounts_config_df["asset_type"].apply(
            lambda x: x.value if x else AssetType.UNKNOWN.value
        )
        accounts_config_df["symbol"] = accounts_config_df["platform_asset_id"]
        trades_df = trades_df.merge(accounts_config_df, on=["account_id", "symbol"], how="left")

    return trades_df


def upsert_trade(trade_data: dict, account_id: str):
    """
    Insert or update a trade based on ticket number.

    trade_data should include fields matching the Trade model (except id/account_id).
    """
    with CacheSessionLocal() as session:
        position_id = trade_data.get("id")
        CoreLogger().info(f"Upserting trade with position_id: {position_id} for account_id: {account_id}")

        trade = session.query(Trade).filter_by(id=position_id, account_id=account_id).first()

        if trade:
            for key, value in trade_data.items():
                if hasattr(trade, key):
                    setattr(trade, key, value)
        else:
            trade = Trade(account_id=account_id, **trade_data)
            session.add(trade)

        session.commit()
        return trade


def delete_trade(ticket: int, account_id: int) -> None:
    """Delete a trade by ticket and account_id."""
    with CacheSessionLocal() as session:
        CoreLogger().info(f"Deleting trade with ticket: {ticket} for account_id: {account_id}")
        session.query(Trade).filter_by(ticket=ticket, account_id=account_id).delete()
        session.commit()


def delete_trades_for_account(account_id: int) -> None:
    """Delete all trades for a given account."""
    with CacheSessionLocal() as session:
        CoreLogger().info(f"Deleting all trades for account_id: {account_id}")
        session.query(Trade).filter_by(account_id=account_id).delete()
        session.commit()


def truncate_table(table_name: str) -> None:
    """Delete all trades in a SQLite-safe way."""
    with CacheSessionLocal() as session:
        CoreLogger().info("Deleting all rows from trades table (SQLite compatible).")
        session.execute(text(f"DELETE FROM {table_name}"))
        session.commit()


def _sync_trades_into_db(days: int) -> None:
    results = []

    for account in AccountService().get_all_accounts():
        try:
            alpha_trades = Mt5Client(account.secret_name).get_history_alpha_trades(account_id=account.uid, days=days)
            CoreLogger().info(f"Fetched {len(alpha_trades)} trades for account {account.friendly_name}")

            count = 0

            for trade in alpha_trades:
                trade_data = {
                    "position_id": trade.id,
                    "order": trade.order,
                    "trade_group": trade.trade_group,
                    "opened_at": trade.opened_at,
                    "closed_at": trade.closed_at,
                    "direction": trade.direction.value,
                    "event": trade.event.value,
                    "size": trade.size,
                    "symbol": trade.symbol,
                    "entry_price": trade.entry_price,
                    "exit_price": trade.exit_price,
                    "profit": trade.profit,
                    "swap": trade.swap,
                    "commission": trade.commission,
                }
                upsert_trade(trade_data, account.uid)
                count += 1

            results.append(f"{account.friendly_name}: {count} trades synced")
        except Exception as error:  # pylint: disable=broad-exception-caught
            CoreLogger().error(f"Error syncing trades for {account.friendly_name}: {error}")
            results.append(f"{account.friendly_name}: sync failed")


def sync_trades_from_all_accounts(days: int = 9999) -> str:
    """
    Syncs MT5 trade history for all accounts.
    Deletes existing trades first.
    Returns a summary string.
    """

    tables = ["cache_trades", "cache_balance_over_time"]
    for table in tables:
        truncate_table(table_name=table)

    _sync_trades_into_db(days)

    return "Successfully synced trades."
