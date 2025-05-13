from sqlalchemy import text

from db.database import SessionLocal
from models.trade_history import Trade
from quant_core.clients.mt5.mt5_client import Mt5Client
from quant_core.services.core_logger import CoreLogger
from services.db.account import get_all_accounts


def get_all_trades() -> list[Trade]:
    """Fetch all trades from the database."""
    with SessionLocal() as session:
        CoreLogger().info("Fetching all trades from the database.")
        return session.query(Trade).all()


def get_trade_by_ticket(ticket: int) -> Trade | None:
    """Fetch a single trade by ticket."""
    with SessionLocal() as session:
        CoreLogger().info(f"Fetching trade with ticket: {ticket}")
        return session.query(Trade).filter_by(ticket=ticket).first()


def upsert_trade(trade_data: dict, account_id: int):
    """
    Insert or update a trade based on ticket number.

    trade_data should include fields matching the Trade model (except id/account_id).
    """
    with SessionLocal() as session:
        ticket = trade_data.get("ticket")
        CoreLogger().info(f"Upserting trade with ticket: {ticket} for account_id: {account_id}")

        trade = session.query(Trade).filter_by(ticket=ticket, account_id=account_id).first()

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
    with SessionLocal() as session:
        CoreLogger().info(f"Deleting trade with ticket: {ticket} for account_id: {account_id}")
        session.query(Trade).filter_by(ticket=ticket, account_id=account_id).delete()
        session.commit()


def delete_trades_for_account(account_id: int) -> None:
    """Delete all trades for a given account."""
    with SessionLocal() as session:
        CoreLogger().info(f"Deleting all trades for account_id: {account_id}")
        session.query(Trade).filter_by(account_id=account_id).delete()
        session.commit()


def truncate_trades_table() -> None:
    """Delete all trades in a SQLite-safe way."""
    with SessionLocal() as session:
        CoreLogger().info("Deleting all rows from trades table (SQLite compatible).")
        session.execute(text("DELETE FROM trades"))
        session.commit()


def sync_trades_from_all_accounts(days: int = 9999) -> str:
    """
    Syncs MT5 trade history for all accounts.
    Deletes existing trades first.
    Returns a summary string.
    """
    results = []

    truncate_trades_table()

    for account in get_all_accounts():
        try:
            data_frame = Mt5Client(account.secret_name).get_history_df(days=days)
            CoreLogger().info(f"Fetched {len(data_frame)} trades for account {account.friendly_name}")

            count = 0

            for _, row in data_frame.iterrows():
                trade_data = {
                    "ticket": row.ticket,
                    "order": row.order,
                    "time": row.time,
                    "type": row.type,
                    "entry": row.entry,
                    "size": row.size,
                    "symbol": row.symbol,
                    "price": row.price,
                    "commission": row.commission,
                    "swap": row.swap,
                    "profit": row.profit,
                    "magic": row.magic,
                    "comment": row.comment,
                }
                upsert_trade(trade_data, account.id)
                count += 1

            results.append(f"{account.friendly_name}: {count} trades synced")
        except Exception as e:
            CoreLogger().error(f"Error syncing trades for {account.friendly_name}: {e}")
            results.append(f"{account.friendly_name}: sync failed")

    return ", ".join(results)
