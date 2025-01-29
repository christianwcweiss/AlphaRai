import abc
import json
from typing import Any, Dict

from quant_core.enums.asset_type import AssetType
from quant_core.enums.platform import Platform
from quant_core.enums.time_period import TimePeriod
from quant_core.enums.trade_direction import TradeDirection


class AlertBody(abc.ABC):
    def __init__(
        self,
        platform: Platform,
        period: TimePeriod,
        direction: TradeDirection,
        asset_type: AssetType,
        time: str,
        strategy_id: str,
    ) -> None:
        self._platform = platform
        self._period = period
        self._direction = direction
        self._asset_type = asset_type
        self._time = time
        self._strategy_id = strategy_id

    @property
    def platform(self) -> Platform:
        return self._platform

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
    def strategy_id(self) -> str:
        return self._strategy_id

    @abc.abstractmethod
    def to_dict(self) -> Dict[str, Any]:
        pass

    def to_sns_body(self) -> str:
        return json.dumps(self.to_dict())
