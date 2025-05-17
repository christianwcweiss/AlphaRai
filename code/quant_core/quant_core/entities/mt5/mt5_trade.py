from datetime import datetime
from typing import Optional


class CompletedMT5Trade:  # pylint: disable=too-many-instance-attributes
    """Represents a completed trade in MetaTrader 5."""

    def __init__(  # pylint: disable=too-many-arguments, too-many-positional-arguments
        self,
        position_id: int,
        ticket: int,
        order: int,
        time: datetime,
        type_code: int,
        entry_type: int,
        size: float,
        symbol: str,
        price: float,
        commission: float,
        swap: float,
        profit: float,
        magic: Optional[int] = None,
        comment: Optional[str] = None,
    ) -> None:
        self._position_id = position_id
        self._ticket = ticket
        self._order = order
        self._time = time
        self._type_code = type_code
        self._entry_type = entry_type
        self._size = size
        self._symbol = symbol
        self._price = price
        self._commission = commission
        self._swap = swap
        self._profit = profit
        self._magic = magic
        self._comment = comment

    @property
    def position_id(self) -> int:
        """Retrieves the position ID associated with the trade."""
        return self._position_id

    @property
    def ticket(self) -> int:
        """Retrieves the ticket associated with the trade."""
        return self._ticket

    @property
    def order(self) -> int:
        """Retrieves the order associated with the trade."""
        return self._order

    @property
    def time(self) -> datetime:
        """Retrieves the time associated with the trade."""
        return self._time

    @property
    def type_code(self) -> int:
        """Retrieves the type code associated with the trade."""
        return self._type_code

    @property
    def entry_type(self) -> int:
        """Retrieves the entry type associated with the trade."""
        return self._entry_type

    @property
    def size(self) -> float:
        """Retrieves the size associated with the trade."""
        return self._size

    @property
    def symbol(self) -> str:
        """Retrieves the symbol associated with the trade."""
        return self._symbol

    @property
    def price(self) -> float:
        """Retrieves the price associated with the trade."""
        return self._price

    @property
    def commission(self) -> float:
        """Retrieves the commission associated with the trade."""
        return self._commission

    @property
    def swap(self) -> float:
        """Retrieves the swap associated with the trade."""
        return self._swap

    @property
    def profit(self) -> float:
        """Retrieves the profit associated with the trade."""
        return self._profit

    @property
    def magic(self) -> Optional[int]:
        """Retrieves the magic number associated with the trade."""
        return self._magic

    @property
    def comment(self) -> Optional[str]:
        """Retrieves the comment associated with the trade."""
        return self._comment
