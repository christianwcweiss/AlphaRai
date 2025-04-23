class MT5TradeSymbolConfig:
    def __init__(self, symbol: str, mt5_symbol: str, size: float, n_staggering: int, decimal_points: int) -> None:
        self._symbol = symbol
        self._mt5_symbol = mt5_symbol
        self._size = size
        self._n_staggering = n_staggering
        self._decimal_points = decimal_points

    @property
    def symbol(self) -> str:
        return self._symbol

    @property
    def mt5_symbol(self) -> str:
        return self._mt5_symbol

    @property
    def size(self) -> float:
        return self._size

    @property
    def n_staggering(self) -> int:
        return self._n_staggering

    @property
    def decimal_points(self) -> int:
        return self._decimal_points
