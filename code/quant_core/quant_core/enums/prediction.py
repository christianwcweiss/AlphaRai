from enum import Enum


class PredictionGoal(Enum):
    CLASSIFICATION = "classification"
    REGRESSION = "regression"


class LabelingMode(Enum):
    RR_RATIO = "rr-ratio"
