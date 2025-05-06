from abc import ABC, abstractmethod
from typing import Optional, Dict, Any
import pandas as pd

from quant_core.enums.trade_direction import TradeDirection


class Confluence(ABC):
    """
    Abstract base class for a Confluence.
    A confluence represents a degree of support (0.0 to 1.0) for a specific trade direction.
    """

    __NAME__: str = "Unnamed Confluence"
    __DESCRIPTION__: str = "No description provided."

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Config may include indicator settings, thresholds, window sizes, etc.
        """
        self.config = config or {}

    @abstractmethod
    def check(self, data_frame: pd.DataFrame, direction: TradeDirection) -> float:
        """
        Evaluate how strongly the confluence supports a trade in the given direction.
        """
        pass

    def explain(self) -> str:
        """
        Optional explanation for UI/debug.
        """
        return f"{self.__NAME__}: {self.__DESCRIPTION__}"
