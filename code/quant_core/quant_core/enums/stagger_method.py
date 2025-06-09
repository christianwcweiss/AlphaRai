from enum import Enum


class StaggerMethod(Enum):
    """Stagger methods for staggering orders or sizes."""

    NONE = "NONE"
    LINEAR = "LINEAR"
    LOGARITHMIC = "LOGARITHMIC"
    FIBONACCI = "FIBONACCI"
