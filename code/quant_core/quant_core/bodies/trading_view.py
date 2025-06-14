from typing import Any, Dict

from quant_core.bodies.alert_body import AlertBody


class TradingViewAlertBody(AlertBody):
    """Alert body for TradingView alerts."""

    ALERT_SOURCE = "Trading View"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "alert_source": self.ALERT_SOURCE,
            "symbol": self.symbol,
            "period": self.period.value,
            "direction": self.direction.value,
            "asset_type": self.asset_type.value,
            "time": self.time,
            "price": self.price,
            "powered_by": self.powered_by,
        }
