from enum import Enum


class TradeMode(Enum):
    """Trade modes for trading platforms."""

    DEFAULT = "DEFAULT"
    GRID = "GRID"

    def to_magic_number(self) -> int:
        """Convert trade mode to magic number."""
        if self == TradeMode.DEFAULT:
            return 0
        if self == TradeMode.GRID:
            return 1

        raise ValueError(f"Unsupported trade mode: {self.name}")
