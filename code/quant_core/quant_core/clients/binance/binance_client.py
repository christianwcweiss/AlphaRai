import json

import boto3
from binance.spot import Spot


class BinanceClient:
    """A client for interacting with MetaTrader 5."""

    def __init__(self, secret_id: str):
        self._secret_id = secret_id
        api_key, secret_id = self._get_binance_credentials()
        self._spot_client = Spot(key=api_key, secret=secret_id)


    def _get_binance_credentials(self) -> tuple[str, str]:
        secrets_manager = boto3.client("secretsmanager", region_name="eu-west-1")
        secret = secrets_manager.get_secret_value(SecretId=self._secret_id)
        secret_dict = json.loads(secret["SecretString"])
        api_key = secret_dict.get("BINANCE_API_KEY")
        secret_key = secret_dict.get("BINANCE_SECRET_KEY")
        if not all([api_key, secret_key]):
            raise ValueError("Missing Binance credentials in secrets manager.")
        return api_key, secret_key


    def get_balance(self) -> float:
        """Get the current balance from Binance."""
        account = self._spot_client.account()

        account.balances = account.get("balances", [])


if __name__ == "__main__":
    # Example usage
    binance_client = BinanceClient(secret_id="your_secret_id_here")
    balance = binance_client.get_balance()

