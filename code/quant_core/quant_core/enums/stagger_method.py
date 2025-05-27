from enum import Enum


class StaggerMethod(Enum):
    """Stagger methods for staggering orders or sizes."""

    NONE = "none"
    LINEAR = "linear"
    LOGARITHMIC = "logarithmic"
    FIBONACCI = "fibonacci"
