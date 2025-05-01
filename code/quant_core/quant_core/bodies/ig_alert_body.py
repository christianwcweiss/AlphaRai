from typing import Dict, Any

from quant_core.bodies.alert_body import AlertBody
from quant_core.enums.asset_type import AssetType
from quant_core.enums.time_period import TimePeriod
from quant_core.enums.trade_direction import TradeDirection


class TradingViewAlertBody(AlertBody):
    ALERT_SOURCE = "TradingView"

    def __init__(self, body: Dict[str, Any]) -> None:
        super().__init__(
            symbol=body["symbol"],
            period=TimePeriod(int(body["period"])),
            direction=TradeDirection(body["direction"].upper()),
            asset_type=AssetType(body["assetType"]),
            time=body["time"],
            powered_by=body.get("poweredBy"),
        )

    def __str__(self) -> str:
        return (
            "TradingViewBody("
            f"source={self.ALERT_SOURCE}, "
            f"symbol={self._symbol}, "
            f"period={self._period}, "
            f"direction={self._direction}, "
            f"time={self._time}, "
            f"asset_type={self._asset_type}"
            f"powered_by={self._powered_by if self._powered_by else 'Not Provided'}"
            ")"
        )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "source": self.ALERT_SOURCE,
            "symbol": self._symbol,
            "period": self._period.value,
            "direction": self._direction.value,
            "time": self._time,
            "assetType": self._asset_type.value,
            "poweredBy": self._powered_by,
        }
