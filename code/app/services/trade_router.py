from typing import List

from entities.trade_details import TradeDetails
from models.main.account import Account
from models.main.account_config import AccountConfig
from models.main.confluence_config import ConfluenceConfig
from quant_core.clients.mt5.mt5_client import Mt5Client
from quant_core.enums.order_type import OrderType
from quant_core.enums.platform import Platform
from quant_core.enums.stagger_method import StaggerMethod
from quant_core.enums.trade_direction import TradeDirection
from quant_core.services.core_logger import CoreLogger
from quant_core.trader.platforms.metatrader import Mt5Trader
from quant_core.utils.trade_utils import calculate_position_size, get_stagger_levels, offset_entry_price
from services.confluence_orchestrator import ConfluenceOrchestrator
from services.db.main.account import AccountService
from services.db.main.account_config import AccountConfigService
from services.db.main.confluence_config import ConfluenceConfigService
from services.magician import Magician
from typing_extensions import Tuple


class TradeRouter:  # pylint: disable=too-few-public-methods
    """Routes trades to the appropriate accounts based on the provided trade signal."""

    def __init__(self, trade: TradeDetails) -> None:
        self.trade = trade

    def _validate_trade(self) -> None:
        """Validates the trade signal."""
        if not self.trade.symbol or not self.trade.direction:
            raise ValueError("Invalid trade signal. Missing symbol or direction.")

        if self.trade.direction is TradeDirection.NEUTRAL:
            raise ValueError(f"Invalid trade direction: {self.trade.direction}. Neutral trades are not allowed.")

    def _get_enabled_accounts(self, trade: TradeDetails) -> List[Tuple[Account, AccountConfig, List[ConfluenceConfig]]]:
        """Gets enabled accounts based on trade signal."""
        accounts = AccountService().get_all_accounts()
        matched_accounts = []

        for account in accounts:
            if not account.enabled:
                CoreLogger().info(f"Account {account.uid} is disabled. Skipping...")
                continue

            if config := AccountConfigService().get_config(account_uid=account.uid, platform_asset_id=trade.symbol):
                if config.enabled_trade_direction.trading_enabled(trade.direction):
                    CoreLogger().info(f"Found config for {account.uid}: {config}")
                    confluence_configs = ConfluenceConfigService().get_configs_by_account(account.uid)
                    matched_accounts.append((account, config, confluence_configs))
                else:
                    CoreLogger().info(f"Config for {account.uid} is disabled. Skipping...")

        return matched_accounts

    def _get_trade_entry_prices_details(self, config: AccountConfig) -> List[float]:
        """Get trade entry details."""

        modified_entry_price = offset_entry_price(self.trade.entry, self.trade.stop_loss, config.entry_offset)

        return get_stagger_levels(
            modified_entry_price,
            self.trade.stop_loss,
            k=config.n_staggers,
            stagger_method=StaggerMethod(config.entry_stagger_method),
        )

    def _get_trade_entry_sizes_details(
        self,
        entry_prices: List[float],
        account: Account,
        config: AccountConfig,
    ) -> List[float]:
        """Get trade entry sizes."""
        single_trade_risk = config.risk_percent / config.n_staggers
        if account.platform is Platform.METATRADER:
            balance = Mt5Client(secret_id=account.secret_name).get_balance()
        else:
            raise NotImplementedError("Only MT5 platform is supported for now.")

        sizes = []

        for entry_price in entry_prices:
            sizes.append(
                calculate_position_size(
                    entry_price=entry_price,
                    stop_loss_price=self.trade.stop_loss,
                    percentage_risk=single_trade_risk,
                    balance=balance,
                    asset_type=config.asset_type,
                    decimal_points=config.decimal_points,
                    lot_size=config.lot_size,
                )
            )

        return sizes

    def _place_mt5_trade(  # pylint: disable=too-many-arguments, too-many-positional-arguments
        self, entry_price: float, size: float, magic: int, trader: Mt5Trader, account_config: AccountConfig
    ) -> None:
        digits = account_config.decimal_points

        trader.open_position(
            symbol=account_config.platform_asset_id,
            order_type=OrderType.LIMIT,
            limit_level=round(entry_price, digits),
            trade_direction=self.trade.direction,
            size=size,
            stop_loss=round(self.trade.stop_loss, digits),
            take_profit=round(self.trade.take_profit_1, digits),
            magic=magic,
        )

    def _place_trades(
        self, account: Account, account_config: AccountConfig, confluence_configs: List[ConfluenceConfig]
    ) -> None:
        CoreLogger().info(f"Placing trade in account {account.uid} for {self.trade.symbol}")

        entry_prices = self._get_trade_entry_prices_details(account_config)
        sizes = self._get_trade_entry_sizes_details(
            entry_prices=entry_prices,
            account=account,
            config=account_config,
        )
        confluences_modifier = ConfluenceOrchestrator(
            confluence_configs=confluence_configs, trade=self.trade
        ).get_confluence_modifier()
        sizes = [round(size * confluences_modifier, 2) for size in sizes]
        trader = Mt5Trader(secret_id=account.secret_name)
        group_magic = Magician().cast(account_config=account_config)

        for entry_price, size in zip(entry_prices, sizes):
            CoreLogger().info(f"Entry price: {entry_price}, Size: {size}, Magic: {group_magic}")
            if account.platform is Platform.METATRADER:
                self._place_mt5_trade(
                    entry_price=entry_price, size=size, magic=group_magic, trader=trader, account_config=account_config
                )

    def route(self) -> None:
        """Routes the trade to the appropriate accounts."""
        self._validate_trade()

        if matched_accounts := self._get_enabled_accounts(self.trade):
            for account, config, confluence_configs in matched_accounts:
                self._place_trades(account, config, confluence_configs)
        else:
            CoreLogger().info(f"No matching configurations found for {self.trade.symbol}")
