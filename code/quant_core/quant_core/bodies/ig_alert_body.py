import json
from typing import Dict, Any

from quant_core.bodies.alert_body import AlertBody
from quant_core.enums.asset_type import AssetType
from quant_core.enums.platform import Platform
from quant_core.enums.time_period import TimePeriod
from quant_core.enums.trade_direction import TradeDirection


class IGAlertBody(AlertBody):
    def __init__(self, body: Dict[str, Any]) -> None:
        super().__init__(
            platform=Platform(body["platform"]),
            period=TimePeriod(int(body["period"])),
            direction=TradeDirection(body["direction"].upper()),
            asset_type=AssetType(body["assetType"]),
            time=body["time"],
            strategy_id=body["strategyId"],
        )
        self._epic = body["epic"]

    @property
    def epic(self) -> str:
        return self._epic

    def __str__(self) -> str:
        return (
            "TradingViewBody("
            f"platform={self._platform.value}, "
            f"period={self._period}, "
            f"direction={self._direction}, "
            f"epic={self._epic}, "
            f"time={self._time}, "
            f"asset_type={self._asset_type})"
            f"strategy_id={self._strategy_id}"
            ")"
        )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "platform": self._platform.value,
            "period": self._period.value,
            "direction": self._direction.value,
            "epic": self._epic,
            "time": self._time,
            "assetType": self._asset_type.value,
            "strategyId": self._strategy_id,
        }
