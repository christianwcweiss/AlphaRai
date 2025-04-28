from entities.trade_details import TradeDetails
from quant_core.enums.time_period import TimePeriod
from services.trade_parser import TradeMessageParser


class TestTradeMessageParser:
    def test_parse_valid_message(self):
        message = """
            JP225USD
            Sell Signal on 15 minute timeframe

            Entry : 33155.8

            Take Profit 1 : 32691.4532201026

            Take Profit 2 : 32227.1064402051

            Take Profit 3 : 31762.7596603077

            Stop Loss : 34084.4935597949

            AI Confidence : 61.5%
        """
        expected_trade_details = TradeDetails(
            symbol="JP225USD",
            direction="Sell",
            timeframe="15",
            entry=33155.8,
            stop_loss=34084.4935597949,
            take_profit_1=32691.4532201026,
            take_profit_2=32227.1064402051,
            take_profit_3=31762.7596603077,
            ai_confidence=61.5,
        )

        trade_details = TradeMessageParser.parse(message)

        assert trade_details.symbol == expected_trade_details.symbol
        assert trade_details.direction == expected_trade_details.direction
        assert trade_details.timeframe is TimePeriod(15)
        assert trade_details.entry == expected_trade_details.entry
        assert trade_details.stop_loss == expected_trade_details.stop_loss
        assert trade_details.take_profit_1 == expected_trade_details.take_profit_1
        assert trade_details.take_profit_2 == expected_trade_details.take_profit_2
        assert trade_details.take_profit_3 == expected_trade_details.take_profit_3
        assert trade_details.ai_confidence == expected_trade_details.ai_confidence
