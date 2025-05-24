from unittest.mock import Mock

import pytest

from entities.trade_details import TradeDetails
from quant_core.enums.trade_direction import TradeDirection
from services.trade_router import TradeRouter


class TestTradeRouter:  # pylint: disable=too-few-public-methods

    @pytest.mark.parametrize(
        "symbol,direction",
        [
            ("USDJPY", TradeDirection.NEUTRAL.value),
            ("", TradeDirection.BUY.value),
            ("", TradeDirection.SELL.value),
            ("", TradeDirection.NEUTRAL.value),
        ],
    )
    def test_invalid_trade(
        self,
        symbol: str,
        direction: str,
    ) -> None:
        """Test invalid trade signal."""
        kwargs = {}
        trade = TradeDetails(
            symbol=symbol,
            direction=direction,
            timeframe="15",
            entry=Mock(),
            stop_loss=Mock(),
            take_profit_1=Mock(),
            take_profit_2=Mock(),
            take_profit_3=Mock(),
            ai_confidence=Mock(),
        )
        router = TradeRouter(trade)

        with pytest.raises(ValueError):
            router.route()
