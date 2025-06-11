from abc import ABC, abstractmethod
from typing import Any, Dict, Optional

import pandas as pd
from quant_core.enums.trade_direction import TradeDirection


class Confluence(ABC):
    """
    Abstract base class for a Confluence.
    A confluence represents a degree of support (0.0 to 1.0) for a specific trade direction.
    """

    __NAME__: str = "Unnamed Confluence"
    __DESCRIPTION__: str = "No description provided."
    __IS_AUTOMATIC__: bool = True

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

    @abstractmethod
    def normalize(self, score: float, min_value: float, max_value: float) -> float:
        """
        Normalize the confluence score to a range of min_value to max_value.
        """

    def explain(self) -> str:
        """
        Optional explanation for UI/debug.
        """
        return f"{self.__NAME__}: {self.__DESCRIPTION__}"
