from entities.trade_details import TradeDetails
from models.account_config import AccountConfig
from quant_core.enums.order_type import OrderType
from quant_core.enums.platform import Platform
from quant_core.enums.stagger_method import StaggerMethod
from quant_core.enums.trade_direction import TradeDirection
from quant_core.services.core_logger import CoreLogger
from quant_core.trader.platforms.metatrader import Mt5Trader
from quant_core.utils.trade_utils import get_stagger_levels, get_stagger_sizes, calculate_position_size
from services.db.account import get_all_accounts
from services.db.account_config import get_configs_by_account_id


class TradeRouter:
    def __init__(self, trade: TradeDetails):
        self.trade = trade

    def route_trade(self):
        if not self.trade.symbol or not self.trade.direction:
            raise ValueError("Invalid trade signal. Missing symbol or direction.")

        accounts = get_all_accounts()
        matched_accounts = []

        for account in accounts:
            if not account.enabled:
                CoreLogger().info(f"Account {account.uid} is disabled. Skipping...")
                continue

            configs = get_configs_by_account_id(account.uid)
            config = next((c for c in configs if c.signal_asset_id.upper() == self.trade.symbol.upper()), None)

            if config and config.enabled:
                CoreLogger().info(f"Successfully matched Account {account.uid} with enabled config")
                matched_accounts.append((account, config))
            else:
                CoreLogger().info(f"Skipping config for {account.uid} (no match or not enabled)")
                continue

        if not matched_accounts:
            CoreLogger().warning(f"No matching configuration found for {self.trade.symbol}")
            return

        for account, config in matched_accounts:
            CoreLogger().info(f"Route Trade to {account.uid}")
            self._place_trades(Platform(account.platform), account.secret_name, config)

    def _place_trades(self, platform: Platform, secret_name: str, config: AccountConfig) -> None:
        CoreLogger().info(f"Placing trade on platform={platform.value}, with config={config}")

        entry_prices = get_stagger_levels(
            self.trade.entry,
            self.trade.stop_loss,
            k=config.n_staggers,
            stagger_method=StaggerMethod(config.entry_stagger_method),
        )

        if platform is Platform.METATRADER:
            CoreLogger().debug("Creating MT5 Trader...")
            trader = Mt5Trader(secret_id=secret_name)
            balance = trader.get_balance()

            CoreLogger().debug("Successfully created MT5 Trader!")

            for i, entry_price in enumerate(entry_prices):
                # Divide total risk across all entries
                individual_risk_percent = config.risk_percent / config.n_staggers

                size = calculate_position_size(
                    entry_price=entry_price,
                    stop_loss_price=self.trade.stop_loss,
                    lot_size=config.lot_size,
                    percentage_risk=individual_risk_percent,
                    balance=balance
                )

                price = round(entry_price, config.decimal_points)
                stop_loss = round(self.trade.stop_loss, config.decimal_points)
                take_profit = round(self.trade.take_profit_1, config.decimal_points)

                CoreLogger().info(f"Placing entry {i + 1} for {self.trade.symbol} at {price} with size {size}")
                CoreLogger().info(
                    f"Risk-Reward Ratio: "
                    f"{abs(self.trade.take_profit_1 - entry_price) / abs(self.trade.stop_loss - entry_price)}"
                )
                CoreLogger().debug(
                    f"Trade {i + 1}: {OrderType.LIMIT} {config.platform_asset_id} at {price}, "
                    f"SL={stop_loss}, TP={take_profit}"
                )

                trader.open_position(
                    symbol=config.platform_asset_id,
                    trade_direction=TradeDirection(self.trade.direction),
                    order_type=OrderType.LIMIT,
                    size=size,
                    stop_loss=stop_loss,
                    take_profit=take_profit,
                    limit_level=price,
                    comment=f"Algopro{self.trade.timeframe.value}",
                )
        else:
            CoreLogger().error(f"Unsupported platform: {platform}")
            return