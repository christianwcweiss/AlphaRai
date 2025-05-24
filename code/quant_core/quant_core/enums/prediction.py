from enum import Enum


class PredictionGoal(Enum):
    """Prediction goals for machine learning models."""

    CLASSIFICATION = "classification"
    REGRESSION = "regression"


class LabelingMode(Enum):
    """Labeling modes for predictions."""

    RR_RATIO = "rr-ratio"
