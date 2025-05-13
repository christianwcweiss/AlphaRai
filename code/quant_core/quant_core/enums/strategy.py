from enum import Enum


class LearningTask(Enum):
    """Learning tasks for machine learning models."""

    CLASSIFICATION = "classification"


class LabelMode(Enum):
    """Labeling modes for predictions."""

    RISK_REWARD = "risk_reward"


class ExitCalculationMode(Enum):
    """Exit calculation modes for risk management and position sizing."""

    ATR = "atr"
    PERCENTAGE = "percentage"


class CalculationMode(Enum):
    """Calculation modes for risk management and position sizing."""

    FIXED = "fixed"
    PERCENTAGE = "percentage"
    PER_TENS = "per_tens"
