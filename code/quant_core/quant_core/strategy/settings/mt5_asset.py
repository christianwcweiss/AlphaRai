from typing import Dict, Any

import yaml

from quant_core.enums.order_type import OrderType
from quant_core.enums.strategy import ExitCalculationMode
from quant_core.enums.time_period import TimePeriod
from quant_core.strategy.setting import StrategySettings


class StrategySettingsMT5Asset(StrategySettings):
    def __init__(
        self,
        symbol: str,
        time_period: TimePeriod,
        minimum_size: float,
        maximum_size: float,
        decimal_digits: int,
        lot_size: float,
    ) -> None:
        self._symbol = symbol
        self._time_period = time_period
        self._minimum_size = minimum_size
        self._maximum_size = maximum_size
        self._decimal_digits = decimal_digits
        self._lot_size = lot_size

    @property
    def symbol(self) -> str:
        return self._symbol

    @property
    def time_period(self) -> TimePeriod:
        return self._time_period

    @property
    def minimum_size(self) -> float:
        return self._minimum_size

    @property
    def maximum_size(self) -> float:
        return self._maximum_size

    @property
    def decimal_digits(self) -> int:
        return self._decimal_digits

    @property
    def lot_size(self) -> float:
        return self._lot_size

    @staticmethod
    def from_yaml(file_path: str) -> "StrategySettingsMT5Asset":
        with open(file_path, "r") as file:
            yaml_data = yaml.safe_load(file)

        return StrategySettingsMT5Asset(
            symbol=yaml_data["ticker"],
            time_period=TimePeriod(yaml_data["time_period"]),
            minimum_size=yaml_data["minimum_size"],
            maximum_size=yaml_data["maximum_size"],
            decimal_digits=yaml_data["decimal_digits"],
            lot_size=yaml_data["lot_size"],
        )

    def to_yaml(self, file_path: str) -> None:
        with open(file_path, "w") as file:
            yaml.dump(self.to_dict(), file)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "symbol": self._symbol,
            "time_period": self._time_period,
            "minimum_size": self._minimum_size,
            "maximum_size": self._maximum_size,
            "decimal_digits": self._decimal_digits,
            "lot_size": self._lot_size,
        }
