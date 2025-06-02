import os
import string
from contextlib import contextmanager
from random import choices
from typing import Optional, List, Any, Union, Type, Generator

import pandas as pd
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeMeta


class Builder:
    @staticmethod
    def build_random_string(length: int = 8) -> str:
        return "".join(choices(string.ascii_lowercase, k=length))

    @staticmethod
    def build_random_int(a: int = 0, b: int = 100) -> int:
        return choices(range(a, b, 1))[0]

    @staticmethod
    def build_random_float(a: float = 0, b: float = 10) -> float:
        return choices([x / 10 for x in range(int(a * 10), int(b * 10), 1)])[0]

    @staticmethod
    def build_random_bool() -> bool:
        return choices([True, False])[0]

    @staticmethod
    def get_random_chart_data_frame(file_name: Optional[str] = None) -> pd.DataFrame:
        data_path = os.path.join(os.path.dirname(__file__), "..", "..", "data")
        files = os.listdir(data_path)
        if file_name:
            assert file_name in files, f"File {file_name} not found in {data_path}"

        file = file_name if file_name else choices(files)[0]

        data_frame = pd.read_csv(
            os.path.join(data_path, file),
        )

        data_frame.columns = ["date", "open", "high", "low", "close", "volume"][: len(data_frame.columns)]
        data_frame["date"] = pd.to_datetime(data_frame["date"])
        data_frame = data_frame.sort_values(by="date")

        return data_frame

    @staticmethod
    def get_random_item(items: List[Any]) -> Any:
        return choices(items)[0]

    @staticmethod
    def get_random_items(items: List[Any], k: int = 5) -> List[Any]:
        return choices(items, k=k)

    @staticmethod
    def build_random_chart_data_frame(
        length: int = 100,
        date_range: Optional[pd.date_range] = None,
        open_prices: Optional[List[float]] = None,
        high_prices: Optional[List[float]] = None,
        low_prices: Optional[List[float]] = None,
        close_prices: Optional[List[float]] = None,
        volume: Optional[List[float]] = None,
        include_volume: bool = True,
    ) -> pd.DataFrame:
        if date_range is None:
            date_range = pd.date_range(start="1/1/2000", periods=length, freq="D")

        if open_prices is None:
            open_prices = [Builder.build_random_float() for _ in range(length)]

        if high_prices is None:
            high_prices = [Builder.build_random_float() for _ in range(length)]

        if low_prices is None:
            low_prices = [Builder.build_random_float() for _ in range(length)]

        if close_prices is None:
            close_prices = [Builder.build_random_float() for _ in range(length)]

        if volume is None:
            volume = [Builder.build_random_float() for _ in range(length)]

        data = {"date": date_range, "open": open_prices, "high": high_prices, "low": low_prices, "close": close_prices}

        assert len(open_prices) == len(high_prices) == len(low_prices) == len(close_prices) == len(volume) == length

        if include_volume:
            data["volume"] = volume
            assert len(data["volume"]) == length

        return pd.DataFrame(data)

    @staticmethod
    def get_trade_history() -> pd.DataFrame:
        data_frame = pd.read_csv(
            os.path.join(os.path.dirname(__file__), "data", "test_trades.csv"),
        )

        return data_frame

    @staticmethod
    @contextmanager
    def temporary_test_db(
        models: Union[Type[DeclarativeMeta], List[Type[DeclarativeMeta]]]
    ) -> Generator[sessionmaker, None, None]:
        if not isinstance(models, list):
            models = [models]

        db_url = "sqlite:///:memory:"

        engine = create_engine(db_url, echo=False)
        SessionLocal = sessionmaker(bind=engine)

        for model in models:
            model.metadata.create_all(bind=engine)

        yield SessionLocal
