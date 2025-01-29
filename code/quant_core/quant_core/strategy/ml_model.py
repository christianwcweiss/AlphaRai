import abc
from typing import Any


class StrategyMLModel(abc.ABC):
    @abc.abstractmethod
    def get_model(self) -> Any:
        pass

    @abc.abstractmethod
    def load_model(self, model_path: str) -> None:
        pass

    @abc.abstractmethod
    def predict(self, data_frame) -> None:
        pass
