import abc
from typing import Dict, Any


class StrategySettings(abc.ABC):
    @staticmethod
    @abc.abstractmethod
    def from_yaml(file_path: str) -> "StrategySettings":
        pass

    @abc.abstractmethod
    def to_yaml(self, file_path: str) -> None:
        pass

    @abc.abstractmethod
    def to_dict(self) -> Dict[str, Any]:
        pass
