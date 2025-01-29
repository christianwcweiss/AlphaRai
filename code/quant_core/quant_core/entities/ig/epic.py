class Epic:
    """The Epic entity represents a trading instrument on the IG platform."""

    def __init__(
        self,
        epic_id: str,
        ticker: str,
        min_trade_size: float,
        rounded_digits: int = 2,
    ) -> None:
        self._epic_id = epic_id
        self._ticker = ticker
        self._min_trade_size = min_trade_size
        self._rounded_digits = rounded_digits

    @property
    def epic_id(self) -> str:
        return self._epic_id

    @property
    def ticker(self) -> str:
        return self._ticker

    @property
    def min_trade_size(self) -> float:
        return self._min_trade_size

    @property
    def rounded_digits(self) -> int:
        return self._rounded_digits

    def __str__(self) -> str:
        return f"{self._ticker} ({self._epic_id})"
