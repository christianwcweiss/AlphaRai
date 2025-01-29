import pytest

from quant_core.clients.ig.ig_api import IGApiPostPositionsOrderBody
from quant_core.enums.ig.time_in_force import TimeInForce
from quant_core.enums.order_type import OrderType
from quant_core.enums.trade_direction import TradeDirection


class TestIGApi:
    pass


class TestBodies:
    @pytest.mark.parametrize(
        "limit_level, limit_distance, force_open",
        [
            (None, None, True),  # Valid case
        ],
    )
    def test_valid_limit_validation(self, limit_level, limit_distance, force_open):
        body = IGApiPostPositionsOrderBody(
            currency_code="USD",
            deal_reference="REF123",
            direction=TradeDirection.BUY,
            epic="EPIC123",
            expiry="DFB",
            force_open=force_open,
            guaranteed_stop=False,
            level=100.0,
            order_type=OrderType.LIMIT,
            quote_id="",
            size=1.0,
            time_in_force=TimeInForce.FILL_OR_KILL,
            trailing_stop=False,
            limit_level=limit_level,
            limit_distance=limit_distance,
        )
        body.validate()  # Should not raise an exception

    @pytest.mark.parametrize(
        "limit_level, limit_distance, force_open",
        [
            (100.0, 50.0, True),  # Both limitLevel and limitDistance set
            (100.0, None, False),  # limitLevel set but forceOpen is False
            (None, 50.0, False),  # limitDistance set but forceOpen is False
        ],
    )
    def test_invalid_limit_validation(self, limit_level, limit_distance, force_open):
        with pytest.raises(ValueError):
            IGApiPostPositionsOrderBody(
                currency_code="USD",
                deal_reference="REF123",
                direction=TradeDirection.BUY,
                epic="EPIC123",
                expiry="DFB",
                force_open=force_open,
                guaranteed_stop=False,
                level=100.0,
                order_type=OrderType.LIMIT,
                quote_id="",
                size=1.0,
                time_in_force=TimeInForce.FILL_OR_KILL,
                trailing_stop=False,
                limit_level=limit_level,
                limit_distance=limit_distance,
            ).validate()

    @pytest.mark.parametrize(
        "stop_level, stop_distance, force_open",
        [
            (None, None, True),  # Valid case
        ],
    )
    def test_valid_stop_validation(self, stop_level, stop_distance, force_open):
        body = IGApiPostPositionsOrderBody(
            currency_code="USD",
            deal_reference="REF123",
            direction=TradeDirection.BUY,
            epic="EPIC123",
            expiry="DFB",
            force_open=force_open,
            guaranteed_stop=False,
            level=100.0,
            order_type=OrderType.LIMIT,
            quote_id="",
            size=1.0,
            time_in_force=TimeInForce.FILL_OR_KILL,
            trailing_stop=False,
            stop_level=stop_level,
            stop_distance=stop_distance,
        )
        body.validate()  # Should not raise an exception

    @pytest.mark.parametrize(
        "stop_level, stop_distance, force_open",
        [
            (100.0, 50.0, True),  # Both stopLevel and stopDistance set
            (100.0, None, False),  # stopLevel set but forceOpen is False
            (None, 50.0, False),  # stopDistance set but forceOpen is False
        ],
    )
    def test_invalid_stop_validation(self, stop_level, stop_distance, force_open):
        with pytest.raises(ValueError):
            IGApiPostPositionsOrderBody(
                currency_code="USD",
                deal_reference="REF123",
                direction=TradeDirection.BUY,
                epic="EPIC123",
                expiry="DFB",
                force_open=force_open,
                guaranteed_stop=False,
                level=100.0,
                order_type=OrderType.LIMIT,
                quote_id="",
                size=1.0,
                time_in_force=TimeInForce.FILL_OR_KILL,
                trailing_stop=False,
                stop_level=stop_level,
                stop_distance=stop_distance,
            ).validate()
