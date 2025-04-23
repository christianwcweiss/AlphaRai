import os

import pandas as pd
from polygon import CryptoClient
from polygon import ForexClient

from quant_core.enums.time_period import TimePeriod


class PolygonClient:

    def __init__(self) -> None:
        self._api_key = os.environ.get("POLYGON_API_KEY")
        self._crypto_client = CryptoClient(self._api_key)
        self._forex_client = ForexClient(self._api_key)

    def get_crypto_data(self, symbol: str, time_period: TimePeriod, n_candles: int = 1300) -> pd.DataFrame:
        start_date = pd.Timestamp.now() - pd.Timedelta(minutes=time_period.value * n_candles)
        end_date = pd.Timestamp.now()

        polygon_data = self._crypto_client.get_aggregate_bars(
            symbol=symbol,
            from_date=start_date,
            to_date=end_date,
            multiplier=time_period.value,
            timespan="minute",
            full_range=True,
            warnings=False,
        )

        polygon_data_frame = pd.DataFrame(polygon_data)

        polygon_data_frame.rename(
            columns={"t": "date", "o": "open", "h": "high", "l": "low", "c": "close", "v": "volume"}, inplace=True
        )

        polygon_data_frame = polygon_data_frame[["date", "open", "high", "low", "close", "volume"]]
        polygon_data_frame["date"] = pd.to_datetime(polygon_data_frame["date"], unit="ms")

        return polygon_data_frame

    def get_forex_data(self, symbol: str, time_period: TimePeriod, n_candles: int = 1300) -> pd.DataFrame:
        start_date = pd.Timestamp.now() - pd.Timedelta(minutes=time_period.value * n_candles)
        end_date = pd.Timestamp.now()

        polygon_data = self._forex_client.get_aggregate_bars(
            symbol=symbol,
            from_date=start_date,
            to_date=end_date,
            multiplier=time_period.value,
            timespan="minute",
            full_range=True,
            warnings=False,
            adjusted=True,
        )

        polygon_data_frame = pd.DataFrame(polygon_data)

        polygon_data_frame.rename(
            columns={"t": "date", "o": "open", "h": "high", "l": "low", "c": "close", "v": "volume"}, inplace=True
        )

        polygon_data_frame = polygon_data_frame[["date", "open", "high", "low", "close", "volume"]]
        polygon_data_frame["date"] = pd.to_datetime(polygon_data_frame["date"], unit="ms")

        return polygon_data_frame
