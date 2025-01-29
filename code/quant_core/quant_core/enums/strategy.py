from enum import Enum


class LearningTask(Enum):
    CLASSIFICATION = "classification"


class LabelMode(Enum):
    RISK_REWARD = "risk_reward"


class ExitCalculationMode(Enum):
    ATR = "atr"
    PERCENTAGE = "percentage"


class CalculationMode(Enum):
    FIXED = "fixed"
    PERCENTAGE = "percentage"
    PER_TENS = "per_tens"
