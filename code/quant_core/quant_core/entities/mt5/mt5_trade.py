from datetime import datetime
from typing import Optional


class MT5Trade:
    def __init__(
        self,
        ticket: int,
        order: int,
        time: datetime,
        trade_type: str,
        size: float,
        symbol: str,
        price: float,
        sl: Optional[float],
        tp: Optional[float],
        commission: float,
        swap: float,
        profit: float,
        magic: Optional[int] = None,
        comment: Optional[str] = None,
    ):
        self._ticket = ticket
        self._order = order
        self._time = time
        self._trade_type = trade_type
        self._size = size
        self._symbol = symbol
        self._price = price
        self._sl = sl
        self._tp = tp
        self._commission = commission
        self._swap = swap
        self._profit = profit
        self._magic = magic
        self._comment = comment

    @property
    def ticket(self):
        return self._ticket

    @property
    def order(self):
        return self._order

    @property
    def time(self):
        return self._time

    @property
    def trade_type(self):
        return self._trade_type

    @property
    def size(self):
        return self._size

    @property
    def symbol(self):
        return self._symbol

    @property
    def price(self):
        return self._price

    @property
    def sl(self):
        return self._sl

    @property
    def tp(self):
        return self._tp

    @property
    def commission(self):
        return self._commission

    @property
    def swap(self):
        return self._swap

    @property
    def profit(self):
        return self._profit

    @property
    def magic(self):
        return self._magic

    @property
    def comment(self):
        return self._comment


class CompletedMT5Trade:
    def __init__(
        self,
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
    ):
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
    def ticket(self):
        return self._ticket

    @property
    def order(self):
        return self._order

    @property
    def time(self):
        return self._time

    @property
    def type_code(self):
        return self._type_code  # MT5 numeric type (0=buy, 1=sell, etc.)

    @property
    def entry_type(self):
        return self._entry_type  # 0=open, 1=close

    @property
    def size(self):
        return self._size

    @property
    def symbol(self):
        return self._symbol

    @property
    def price(self):
        return self._price

    @property
    def commission(self):
        return self._commission

    @property
    def swap(self):
        return self._swap

    @property
    def profit(self):
        return self._profit

    @property
    def magic(self):
        return self._magic

    @property
    def comment(self):
        return self._comment
