from typing import Any

import pandas as pd

from quant_core.strategy.ml_model import StrategyMLModel


class StrategyMLModelXGBoost(StrategyMLModel):
    def __init__(self) -> None:
        pass

    def get_model(self) -> Any:
        pass

    def load_model(self, model_path: str) -> None:
        pass

    def predict(self, data_frame: pd.DataFrame) -> None:
        pass
