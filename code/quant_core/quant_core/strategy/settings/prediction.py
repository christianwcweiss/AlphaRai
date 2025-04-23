from typing import Dict, Any, Union, LiteralString

import yaml

from quant_core.enums.prediction import PredictionGoal, LabelingMode
from quant_core.strategy.setting import StrategySettings


class StrategySettingsPrediction(StrategySettings):
    def __init__(
        self,
        mode: PredictionGoal,
        horizon: int,
        labeling_mode: LabelingMode,
        threshold: float,
        threshold_strong: float,
    ) -> None:
        self._mode = mode
        self._horizon = horizon
        self._labeling_mode = labeling_mode
        self._threshold = threshold
        self._threshold_strong = threshold_strong

    @property
    def mode(self) -> PredictionGoal:
        return self._mode

    @property
    def horizon(self) -> int:
        return self._horizon

    @property
    def labeling_mode(self) -> LabelingMode:
        return self._labeling_mode

    @property
    def threshold(self) -> float:
        return self._threshold

    @property
    def threshold_strong(self) -> float:
        return self._threshold_strong

    @staticmethod
    def from_yaml(file_path: Union[LiteralString, str, bytes]) -> "StrategySettingsPrediction":
        with open(file_path, "r") as file:
            yaml_data = yaml.safe_load(file)

        return StrategySettingsPrediction(
            mode=PredictionGoal(yaml_data["mode"]),
            horizon=yaml_data["horizon"],
            labeling_mode=LabelingMode(yaml_data["labeling_mode"]),
            threshold=yaml_data["threshold"],
            threshold_strong=yaml_data["threshold_strong"],
        )

    def to_yaml(self, file_path: str) -> None:
        with open(file_path, "w") as file:
            yaml.dump(self.to_dict(), file)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "mode": self._mode.value,
            "horizon": self._horizon,
            "labeling_mode": self._labeling_mode.value,
            "threshold": self._threshold,
            "threshold_strong": self._threshold_strong,
        }
