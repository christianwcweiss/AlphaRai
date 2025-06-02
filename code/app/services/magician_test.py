import pytest
from models.main.account_config import AccountConfig
from quant_core.enums.trade_mode import TradeMode
from services.magician import Magician


class TestMagician:
    """
    A class defining the magic of a trade to be placed and looked up later.
    """

    @pytest.mark.parametrize("trade_mode", list(TradeMode))
    def test_random_number_is_created(self, trade_mode) -> None:
        """
        Test that a random number is created.
        """
        random_number = Magician().cast(account_config=AccountConfig(signal_asset_id="EURUSD", mode=trade_mode.value))

        assert isinstance(random_number, int)
        assert random_number % 10 == trade_mode.value
