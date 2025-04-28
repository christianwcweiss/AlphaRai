from typing import Dict, Any, Union, LiteralString

import yaml

from quant_core.enums.order_type import OrderType
from quant_core.strategy.setting import StrategySettings


class StrategySettingsPositionEntry(StrategySettings):
    def __init__(
        self,
        mode: OrderType,
    ) -> None:
        self._mode = mode

    @property
    def mode(self) -> OrderType:
        return self._mode

    @staticmethod
    def from_yaml(file_path: Union[LiteralString, str, bytes]) -> "StrategySettingsPositionEntry":
        with open(file_path, "r") as file:
            yaml_data = yaml.safe_load(file)

        return StrategySettingsPositionEntry(
            mode=OrderType(yaml_data["mode"]),
        )

    def to_yaml(self, file_path: str) -> None:
        with open(file_path, "w") as file:
            yaml.dump(self.to_dict(), file)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "mode": self._mode.value,
        }
