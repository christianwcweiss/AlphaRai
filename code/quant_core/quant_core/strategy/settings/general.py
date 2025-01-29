
from typing import Dict, Any, Union, LiteralString

import yaml

from quant_core.strategy.setting import StrategySettings


class StrategySettingsGeneral(StrategySettings):
    def __init__(
        self,
        trading_enabled: bool,
        signal_enabled: bool,
    ) -> None:
        self._trading_enabled = trading_enabled
        self._signal_enabled = signal_enabled

    @property
    def trading_enabled(self) -> bool:
        return self._trading_enabled

    @property
    def signal_enabled(self) -> bool:
        return self._signal_enabled

    @staticmethod
    def from_yaml(file_path: Union[LiteralString, str, bytes]) -> "StrategySettingsGeneral":
        with open(file_path, "r") as file:
            yaml_data = yaml.safe_load(file)

        return StrategySettingsGeneral(
            trading_enabled=yaml_data["trading_enabled"],
            signal_enabled=yaml_data["signal_enabled"],
        )

    def to_yaml(self, file_path: str) -> None:
        with open(file_path, "w") as file:
            yaml.dump(self.to_dict(), file)


    def to_dict(self) -> Dict[str, Any]:
        return {
            "trading_enabled": self._trading_enabled,
            "signal_enabled": self._signal_enabled,
        }
