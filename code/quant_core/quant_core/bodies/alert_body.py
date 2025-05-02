import abc
import json
from typing import Any, Dict, Optional

from quant_core.enums.asset_type import AssetType
from quant_core.enums.time_period import TimePeriod
from quant_core.enums.trade_direction import TradeDirection


class AlertBody(abc.ABC):
    ALERT_SOURCE: str

    def __init__(
        self,
        symbol: str,
        period: TimePeriod,
        direction: TradeDirection,
        asset_type: AssetType,
        time: str,
        powered_by: Optional[str] = None,
    ) -> None:
        self._symbol = symbol
        self._period = period
        self._direction = direction
        self._asset_type = asset_type
        self._time = time
        self._powered_by = powered_by

    @property
    def symbol(self) -> str:
        return self._symbol

    @property
    def period(self) -> TimePeriod:
        return self._period

    @property
    def direction(self) -> TradeDirection:
        return self._direction

    @property
    def asset_type(self) -> AssetType:
        return self._asset_type

    @property
    def time(self) -> str:
        return self._time

    @property
    def powered_by(self) -> Optional[str]:
        return self._powered_by

    @abc.abstractmethod
    def to_dict(self) -> Dict[str, Any]:
        pass

    def to_sns_body(self) -> str:
        return json.dumps(self.to_dict())
