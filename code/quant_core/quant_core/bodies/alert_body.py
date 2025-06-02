import abc
import json
from typing import Any, Dict, Optional

from quant_core.enums.asset_type import AssetType
from quant_core.enums.time_period import TimePeriod
from quant_core.enums.trade_direction import TradeDirection


class AlertBody(abc.ABC):
    """Abstract base class for alert bodies."""

    ALERT_SOURCE: str

    def __init__(  # pylint: disable=too-many-arguments, too-many-positional-arguments
        self,
        symbol: str,
        period: TimePeriod,
        direction: TradeDirection,
        asset_type: AssetType,
        time: str,
        price: Optional[float] = None,
        powered_by: Optional[str] = None,
    ) -> None:
        self._symbol = symbol
        self._period = period
        self._direction = direction
        self._asset_type = asset_type
        self._time = time
        self._price = price
        self._powered_by = powered_by

    @property
    def symbol(self) -> str:
        """Symbol of the alert."""
        return self._symbol

    @property
    def period(self) -> TimePeriod:
        """Period of the alert."""
        return self._period

    @property
    def direction(self) -> TradeDirection:
        """Direction of the alert."""
        return self._direction

    @property
    def asset_type(self) -> AssetType:
        """Asset type of the alert."""
        return self._asset_type

    @property
    def time(self) -> str:
        """Time of the alert."""
        return self._time

    @property
    def price(self) -> Optional[float]:
        """Price of the alert."""
        return self._price

    @property
    def powered_by(self) -> Optional[str]:
        """Source of the alert."""
        return self._powered_by

    @abc.abstractmethod
    def to_dict(self) -> Dict[str, Any]:
        """Convert the alert body to a dictionary."""

    def to_sns_body(self) -> str:
        """Convert the alert body to a JSON string for SNS."""
        return json.dumps(self.to_dict())
