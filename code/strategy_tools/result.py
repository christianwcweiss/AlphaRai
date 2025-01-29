import json
import os
from typing import Dict, Any, List
from uuid import uuid4

import pandas as pd
from sklearn.metrics import confusion_matrix

from back_tester import BacktestTrade
from quant_core.entities.strategy_configuration import StrategyConfiguration


class TradeSimulatorResult:
    def __init__(
        self,
        trades: List[BacktestTrade],
    ) -> None:
        self._trades = trades

    def to_dict(self) -> Dict[str, Any]:
        return {
            "trades": [trade.to_dict() for trade in self._trades],
        }


class ModelResult:
    def __init(
        self,
        model_name: str,
        accuracy: float,
        auc: float,
        recall: float,
        precision: float,
        f1: float,
        kappa: float,
        mcc: float,
        tt_seconds: float,
    ) -> None:
        self._model_name = model_name
        self._accuracy = accuracy
        self._auc = auc
        self._recall = recall
        self._precision = precision
        self._f1 = f1
        self._kappa = kappa
        self._mcc = mcc
        self._tt_seconds = tt_seconds

    @property
    def model_name(self) -> str:
        return self._model_name

    @property
    def accuracy(self) -> float:
        return self._accuracy

    @property
    def auc(self) -> float:
        return self._auc

    @property
    def recall(self) -> float:
        return self._recall

    @property
    def precision(self) -> float:
        return self._precision

    @property
    def f1(self) -> float:
        return self._f1

    @property
    def kappa(self) -> float:
        return self._kappa

    @property
    def mcc(self) -> float:
        return self._mcc

    @property
    def tt_seconds(self) -> float:
        return self._tt_seconds

    def to_dict(self) -> dict:
        return {
            "model_name": self._model_name,
            "accuracy": self._accuracy,
            "auc": self._auc,
            "recall": self._recall,
            "precision": self._precision,
            "f1": self._f1,
            "kappa": self._kappa,
            "mcc": self._mcc,
            "tt_seconds": self._tt_seconds,
        }

    def __str__(self) -> str:
        return "\n".join(f"{k}: {v}" for k, v in self.to_dict().items())


class StatsResult:
    def __init__(self, df: pd.DataFrame) -> None:
        self.df = df.copy()

        self.classes = [1, 2, 3, 4, 5]

        self.confusion = confusion_matrix(self.df["label_value"], self.df["prediction"], labels=self.classes)

        self.false_positives = {}
        self.false_negatives = {}
        for c in self.classes:
            fp = ((self.df["prediction"] == c) & (self.df["label_value"] != c)).sum()
            fn = ((self.df["prediction"] != c) & (self.df["label_value"] == c)).sum()
            self.false_positives[c] = int(fp)
            self.false_negatives[c] = int(fn)

        def directional_error(row):
            actual = row["label_value"]
            pred = row["prediction"]
            if actual == pred:
                return 0
            if actual == 3 or pred == 3:
                return abs(pred - actual)
            if (actual < 3 and pred > 3) or (actual > 3 and pred < 3):
                return 2 * abs(pred - actual)
            return abs(pred - actual)

        self.df["directional_error"] = self.df.apply(directional_error, axis=1)
        self.mean_directional_error = self.df["directional_error"].mean()

        self.predicted_distribution = self.df["prediction"].value_counts().sort_index().to_dict()
        self.true_distribution = self.df["label_value"].value_counts().sort_index().to_dict()

    def to_dict(self) -> dict:
        return {
            "confusion_matrix": self.confusion.tolist(),
            "false_positives": self.false_positives,
            "false_negatives": self.false_negatives,
            "mean_directional_error": self.mean_directional_error,
            "predicted_distribution": self.predicted_distribution,
            "true_distribution": self.true_distribution,
        }

    def __str__(self) -> str:
        return "\n".join(f"{k}: {v}" for k, v in self.to_dict().items())


class BacktestResult:
    def __init__(self, store_path: str) -> None:
        self._id = str(uuid4())
        self._store_path = store_path
        self._strategy = None
        self._model_results = []
        self._trade_simulator_results = None

    @property
    def backtest_id(self) -> str:
        return self._id

    def add_strategy(self, strategy: StrategyConfiguration) -> None:
        self._strategy = strategy

    def add_model_result(self, model_result: ModelResult) -> None:
        self._model_results.append(model_result)

    def add_trade_simulator_result(self, trade_simulator_result: TradeSimulatorResult) -> None:
        self._trade_simulator_results = trade_simulator_result

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self._id,
            "strategy": self._strategy.to_dict(),
            "model_results": [result.to_dict() for result in self._model_results],
            "trade_simulator_results": self._trade_simulator_results.to_dict(),
        }

    def store(self) -> None:
        if not os.path.exists(self._store_path):
            os.makedirs(self._store_path)

        with open(f"{self._store_path}/{self._id}.json", "w") as f:
            json.dump(self.to_dict(), f)

    def generate_graphs(self, directory: str) -> None:
        pass

    def to_report_data(self, directory: str) -> Dict[str, Any]:
        pass
