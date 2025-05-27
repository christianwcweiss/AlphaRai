from datetime import datetime
from random import randint

from models.main.account_config import AccountConfig
from quant_core.enums.trade_mode import TradeMode


class Magician:  # pylint: disable=too-few-public-methods
    """
    A class defining the magic of a trade to be placed and looked up later.
    """

    def _cast_mode_number(self, account_config: AccountConfig) -> int:
        """
        Casts a magic number based on the mode of the trade.
        """
        return TradeMode(account_config.mode).value

    def cast(self, account_config: AccountConfig) -> int:
        """
        Casts a magic number for the trade.

        9 digits are used in total:

        1-3 random numbers
        4-6 hash of symbol and date
        7-8 salt
        9 mode number

        """
        random_prefix = randint(100, 999)
        salt = randint(100, 999)
        hash_part = hash(f"{account_config.signal_asset_id}{datetime.now()}") % 1000
        mode_number = self._cast_mode_number(account_config)
        magic_number = f"{random_prefix}{hash_part}{salt}{mode_number}"

        return int(magic_number)
