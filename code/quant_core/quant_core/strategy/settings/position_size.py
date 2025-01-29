from typing import Dict, Any

import yaml

from quant_core.enums.strategy import CalculationMode
from quant_core.strategy.setting import StrategySettings


class StrategySettingsPositionSize(StrategySettings):
    def __init__(
        self,
        mode: CalculationMode,
        value: float,
    ) -> None:
        self._mode = mode
        self._value = value

    @property
    def mode(self) -> CalculationMode:
        return self._mode

    @property
    def value(self) -> float:
        return self._value


    @staticmethod
    def from_yaml(file_path: str) -> "StrategySettingsPositionSize":
        with open(file_path, "r") as file:
            yaml_data = yaml.safe_load(file)

        return StrategySettingsPositionSize(
            mode=CalculationMode(yaml_data["mode"]),
            value=yaml_data["value"],
        )

    def to_yaml(self, file_path: str) -> None:
        with open(file_path, "w") as file:
            yaml.dump(self.to_dict(), file)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "mode": self._mode.value,
            "value": self._value,
        }
