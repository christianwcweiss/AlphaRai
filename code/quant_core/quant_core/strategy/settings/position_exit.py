from typing import Dict, Any

import yaml

from quant_core.enums.strategy import ExitCalculationMode
from quant_core.strategy.setting import StrategySettings


class StrategySettingsPositionExit(StrategySettings):
    def __init__(
        self,
        mode: ExitCalculationMode,
        value: float,
        risk_modifier: float = 1.0,
        reward_modifier: float = 1.0,
        strong_sell_modifier: float = 1.0,
        sell_modifier: float = 1.0,
        buy_modifier: float = 1.0,
        strong_buy_modifier: float = 1.0,
    ) -> None:
        self._mode = mode
        self._value = value
        self._risk_modifier = risk_modifier
        self._reward_modifier = reward_modifier
        self._strong_sell_modifier = strong_sell_modifier
        self._sell_modifier = sell_modifier
        self._buy_modifier = buy_modifier
        self._strong_buy_modifier = strong_buy_modifier

    @property
    def mode(self) -> ExitCalculationMode:
        return self._mode

    @property
    def value(self) -> float:
        return self._value

    @property
    def risk_modifier(self) -> float:
        return self._risk_modifier

    @property
    def reward_modifier(self) -> float:
        return self._reward_modifier

    @property
    def strong_sell_modifier(self) -> float:
        return self._strong_sell_modifier

    @property
    def sell_modifier(self) -> float:
        return self._sell_modifier

    @property
    def buy_modifier(self) -> float:
        return self._buy_modifier

    @property
    def strong_buy_modifier(self) -> float:
        return self._strong_buy_modifier

    @staticmethod
    def from_yaml(file_path: str) -> "StrategySettingsPositionExit":
        with open(file_path, "r") as file:
            yaml_data = yaml.safe_load(file)

        return StrategySettingsPositionExit(
            mode=ExitCalculationMode(yaml_data["mode"]),
            value=yaml_data["value"],
            risk_modifier=yaml_data.get("risk_modifier", 1.0),
            reward_modifier=yaml_data.get("reward_modifier", 1.0),
            strong_sell_modifier=yaml_data.get("strong_sell_modifier", 1.0),
            sell_modifier=yaml_data.get("sell_modifier", 1.0),
            buy_modifier=yaml_data.get("buy_modifier", 1.0),
            strong_buy_modifier=yaml_data.get("strong_buy_modifier", 1.0),
        )

    def to_yaml(self, file_path: str) -> None:
        with open(file_path, "w") as file:
            yaml.dump(self.to_dict(), file)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "mode": self._mode.value,
            "value": self._value,
            "risk_modifier": self._risk_modifier,
            "reward_modifier": self._reward_modifier,
            "strong_sell_modifier": self._strong_sell_modifier,
            "sell_modifier": self._sell_modifier,
            "buy_modifier": self._buy_modifier,
            "strong_buy_modifier": self._strong_buy_modifier,
        }
