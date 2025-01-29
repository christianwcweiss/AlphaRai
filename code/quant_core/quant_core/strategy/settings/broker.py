
from typing import Dict, Any

import yaml

from quant_core.enums.platform import Platform
from quant_core.enums.order_type import OrderType
from quant_core.enums.strategy import ExitCalculationMode
from quant_core.strategy.setting import StrategySettings


class StrategySettingsPlatform(StrategySettings):
    def __init__(
        self,
        platform: Platform,
        secrets_manager_secret_id: str,
    ) -> None:
        self._platform = platform
        self._secrets_manager_secret_id = secrets_manager_secret_id

    @property
    def platform(self) -> Platform:
        return self._platform

    @property
    def secrets_manager_secret_id(self) -> str:
        return self._secrets_manager_secret_id

    @staticmethod
    def from_yaml(file_path: str) -> "StrategySettingsPlatform":
        with open(file_path, "r") as file:
            yaml_data = yaml.safe_load(file)

        return StrategySettingsPlatform(
            platform=Platform(yaml_data["platform"]),
            secrets_manager_secret_id=yaml_data["secrets_manager_secret_id"],
        )

    def to_yaml(self, file_path: str) -> None:
        with open(file_path, "w") as file:
            yaml.dump(self.to_dict(), file)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "broker": self._platform.value,
            "secrets_manager_secret_id": self._secrets_manager_secret_id,
        }
