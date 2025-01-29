from entities.trade_details import TradeDetails
from models.trade_config import TradeConfig
from quant_core.enums.order_type import OrderType
from quant_core.enums.platform import Platform
from quant_core.enums.stagger_method import StaggerMethod
from quant_core.enums.trade_direction import TradeDirection
from quant_core.services.core_logger import CoreLogger
from quant_core.trader.platforms.ig import IgTrader
from quant_core.trader.platforms.metatrader import Mt5Trader
from quant_core.utils.trade_utils import get_stagger_levels, get_stagger_sizes
from services.credential_settings import get_all_credential_settings
from services.trade_config import get_configs_by_uid


class TradeRouter:
    def __init__(self, trade: TradeDetails):
        self.trade = trade

    def route_trade(self):
        if not self.trade.symbol or not self.trade.direction:
            raise ValueError("Invalid trade signal. Missing symbol or direction.")

        accounts = get_all_credential_settings()
        matched_accounts = []

        for account in accounts:
            if not account.enabled:
                CoreLogger().info(f"Account {account.uid} is disabled. Skipping...")
                continue

            configs = get_configs_by_uid(account.uid)
            config = next((c for c in configs if c.signal_asset_id.upper() == self.trade.symbol.upper()), None)

            if config:
                CoreLogger().info(f"Successfully matched Account {account.uid}")
                matched_accounts.append((account, config))

        if not matched_accounts:
            CoreLogger().warning(f"No matching configuration found for {self.trade.symbol}")
            return

        for account, config in matched_accounts:
            CoreLogger().info(f"Route Trade to {account.uid}")
            self._place_trades(Platform(account.platform), account.secret_name, config)

    def _place_trades(self, platform: Platform, secret_name: str, config: TradeConfig) -> None:
        CoreLogger().info(
            f"Placing trade on platform={platform.value}, with config={config}"
        )
        entry_prices = get_stagger_levels(
            self.trade.entry,
            self.trade.stop_loss,
            k=config.n_staggers,
            stagger_method=StaggerMethod(config.entry_stagger_method)
        )
        entry_sizes = get_stagger_sizes(
            config.size,
            config.size,
            k=config.n_staggers,
            stagger_method=StaggerMethod(config.size_stagger_method)
        )

        if platform is Platform.METATRADER:
            CoreLogger().debug("Creating MT5 Trader...")
            trader = Mt5Trader(secret_id=secret_name)
            CoreLogger().debug("Successfully created MT5 Trader!")
            CoreLogger().debug(f"Converting order type to MT5 format...")
            CoreLogger().debug(f"Successfully converted order type to MT5 format...")
            for i, (size, entry_price) in enumerate(zip(entry_sizes, entry_prices)):
                CoreLogger().info(
                    f"Placing entry {i+1} for {self.trade.symbol} at {entry_price} with size {size}"
                )
                CoreLogger().info(
                    f"Risk-Reward Ratio: {abs(self.trade.take_profit_1 - entry_price) / abs(self.trade.stop_loss - entry_price)}"
                )
                size = round(size, 2)
                price = round(entry_price, config.decimal_points)
                stop_loss = round(self.trade.stop_loss, config.decimal_points)
                take_profit = round(self.trade.take_profit_1, config.decimal_points)

                CoreLogger().debug(f"Trade {i+1}: {OrderType.LIMIT} {config.platform_asset_id} at {price}, SL={stop_loss}, TP={take_profit}")

                trader.open_position(
                    symbol=config.platform_asset_id,
                    trade_direction=TradeDirection(self.trade.direction),
                    order_type=OrderType.LIMIT,
                    size=size,
                    stop_loss=stop_loss,
                    take_profit=take_profit,
                    limit_level=price,
                    comment=f"Algopro{self.trade.timeframe.value}"
                )
        elif platform is Platform.IG:
            CoreLogger().debug("Creating IG Trader...")
            trader = IgTrader(secret_id=secret_name)
            CoreLogger().debug("Successfully created IG Trader!")
            for i, (size, entry_price) in enumerate(zip(entry_sizes, entry_prices)):
                CoreLogger().info(
                    f"Placing entry {i+1} for {self.trade.symbol} at {entry_price} with size {size}"
                )
                CoreLogger().info(
                    f"Risk-Reward Ratio: {abs(self.trade.take_profit_1 - entry_price) / abs(self.trade.stop_loss - entry_price)}"
                )
                size = round(size, 2)
                price = round(entry_price, config.decimal_points)
                stop_loss = round(self.trade.stop_loss, config.decimal_points)
                take_profit = round(self.trade.take_profit_1, config.decimal_points)

                CoreLogger().debug(f"Trade {i+1}: {config.platform_asset_id} at {price}, SL={stop_loss}, TP={take_profit}")

                trader.open_position(
                    symbol=config.platform_asset_id,
                    trade_direction=TradeDirection(TradeDirection(self.trade.direction).to_ig()),
                    order_type=OrderType.LIMIT,
                    size=size,
                    stop_loss=stop_loss,
                    take_profit=take_profit,
                    limit_level=price
                )
        else:
            CoreLogger().error(f"Unsupported platform: {platform}")
            return



