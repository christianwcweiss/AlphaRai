from enum import Enum


class Feature(Enum):
    """Feature types for technical analysis and data processing."""

    ATR = "atr"
    SMOOTHED_HA = "smoothed_ha"
    SHARPE_RATIO = "sharpe_ratio"
    SORTINO_RATIO = "sortino_ratio"
    SQUEEZE_MOMENTUM = "squeeze_momentum"
    SUPER_TREND = "super_trend"
    ADAPTIVE_SUPER_TREND = "adaptive_super_trend"
