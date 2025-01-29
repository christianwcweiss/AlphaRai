
from typing import Dict, Any

import yaml

from quant_core.enums.order_type import OrderType
from quant_core.enums.strategy import ExitCalculationMode
from quant_core.strategy.setting import StrategySettings


class StrategySettingsIGEpic(StrategySettings):
    def __init__(
        self,
        epic_id: str,
        currency_code: str,
        resolution: str,
        minimum_size: float,
        maximum_size: float,
        decimal_digits: int,
        lot_size: float,
    ) -> None:
        self._epic_id = epic_id
        self._currency_code = currency_code
        self._resolution = resolution
        self._minimum_size = minimum_size
        self._maximum_size = maximum_size
        self._decimal_digits = decimal_digits
        self._lot_size = lot_size

    @property
    def epic_id(self) -> str:
        return self._epic_id

    @property
    def currency_code(self) -> str:
        return self._currency_code

    @property
    def resolution(self) -> str:
        return self._resolution

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
    def from_yaml(file_path: str) -> "StrategySettingsIGEpic":
        with open(file_path, "r") as file:
            yaml_data = yaml.safe_load(file)

        return StrategySettingsIGEpic(
            epic_id=yaml_data["epic"],
            currency_code=yaml_data["currency_code"],
            resolution=yaml_data["resolution"],
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
            "epic_id": self._epic_id,
            "currency_code": self._currency_code,
            "resolution": self._resolution,
            "minimum_size": self._minimum_size,
            "maximum_size": self._maximum_size,
            "decimal_digits": self._decimal_digits,
            "lot_size": self._lot_size,
        }
