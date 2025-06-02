import json
import os

import boto3
import pandas as pd
from polygon import CryptoClient, ForexClient, StocksClient
from quant_core.enums.time_period import TimePeriod
from quant_core.services.core_logger import CoreLogger


class PolygonClient:
    """Polygon.io client for fetching market data."""

    def __init__(self) -> None:
        self._api_key = os.environ.get("POLYGON_API_KEY")
        if not self._api_key:
            self._api_key = json.loads(self._load_from_secret_manager(secret_name="POLYGON_API_KEY"))["POLYGON_API_KEY"]
            if not self._api_key:
                CoreLogger().warning("No API key found. Full functionality will not be available.")

        self._crypto_client = CryptoClient(self._api_key)
        self._forex_client = ForexClient(self._api_key)
        self._stock_client = StocksClient(self._api_key)

    def _load_from_secret_manager(self, secret_name: str) -> str:
        secretsmanager_client = boto3.client("secretsmanager")
        try:
            secret_value = secretsmanager_client.get_secret_value(SecretId=secret_name)
            if "SecretString" in secret_value:
                return secret_value["SecretString"]

            raise ValueError(f"Secret {secret_name} not found.")
        except ValueError as error:
            raise ValueError from error

    def get_crypto_data(self, symbol: str, time_period: TimePeriod, n_candles: int = 2000) -> pd.DataFrame:
        """Get crypto data from Polygon.io."""
        start_date = pd.Timestamp.now() - pd.Timedelta(minutes=time_period.value * n_candles)
        end_date = pd.Timestamp.now() + pd.Timedelta(minutes=time_period.value)

        polygon_data = self._crypto_client.get_aggregate_bars(
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

    def get_forex_data(self, symbol: str, time_period: TimePeriod, n_candles: int = 2000) -> pd.DataFrame:
        """Get forex data from Polygon.io."""
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

        CoreLogger().info(f"Polygon DataFrame: {polygon_data_frame.head()}")
        polygon_data_frame.rename(
            columns={"t": "date", "o": "open", "h": "high", "l": "low", "c": "close", "v": "volume"}, inplace=True
        )

        polygon_data_frame = polygon_data_frame[["date", "open", "high", "low", "close", "volume"]]
        polygon_data_frame["date"] = pd.to_datetime(polygon_data_frame["date"], unit="ms")

        return polygon_data_frame

    def get_stock_data(self, symbol: str, time_period: TimePeriod, n_candles: int = 2000) -> pd.DataFrame:
        """Get stock data from Polygon.io."""
        start_date = pd.Timestamp.now() - pd.Timedelta(minutes=time_period.value * n_candles)
        end_date = pd.Timestamp.now()

        polygon_data = self._stock_client.get_aggregate_bars(
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
        polygon_data_frame = polygon_data_frame.astype(
            {"open": "float64", "high": "float64", "low": "float64", "close": "float64", "volume": "int64"}
        )

        return polygon_data_frame
