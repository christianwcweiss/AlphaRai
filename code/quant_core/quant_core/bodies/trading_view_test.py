import json

import boto3
from moto import mock_aws

from quant_core.bodies.trading_view import TradingViewAlertBody
from quant_core.enums.asset_type import AssetType
from quant_core.enums.time_period import TimePeriod
from quant_core.enums.trade_direction import TradeDirection
from quant_dev.builder import Builder


class TestTradingViewAlertBody:
    """Alert body for TradingView alerts."""

    @mock_aws
    def test_to_sns(self) -> None:
        """Test conversion to SNS format."""
        sns_client = boto3.client("sns")
        topic_id = sns_client.create_topic(Name="test-topic")["TopicArn"]
        symbol = Builder.build_random_string()
        period = Builder.get_random_item(list(TimePeriod))
        direction = Builder.get_random_item(list(TradeDirection))
        asset_type = Builder.get_random_item(list(AssetType))
        time = Builder.build_random_string()
        powered_by = Builder.build_random_string()

        alert_body = TradingViewAlertBody(
            symbol=symbol,
            period=period,
            direction=direction,
            asset_type=asset_type,
            time=time,
            powered_by=powered_by,
        )

        sns_alert = alert_body.to_sns_body()
        assert isinstance(sns_alert, str)

        sns_client.publish(TopicArn=topic_id, Message=sns_alert)

        assert json.loads(sns_alert) == {
            "alert_source": TradingViewAlertBody.ALERT_SOURCE,
            "symbol": symbol,
            "period": period.value,
            "direction": direction.value,
            "asset_type": asset_type.value,
            "time": time,
            "powered_by": powered_by,
        }
        assert json.loads(sns_alert) == alert_body.to_dict()
