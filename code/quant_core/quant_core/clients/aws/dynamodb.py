from typing import Any, Dict

import boto3


class DynamoDBClient:
    def __init__(self) -> None:
        self._client = boto3.client("dynamodb")

    def get_item(self, table_name: str, key: Dict[str, Any]) -> Dict[str, Any]:
        return self._client.get_item(TableName=table_name, Key=key)

    def put_item(self, table_name: str, item: Dict[str, Any]) -> Dict[str, Any]:
        return self._client.put_item(TableName=table_name, Item=item)

    def delete_item(self, table_name: str, key: Dict[str, Any]) -> Dict[str, Any]:
        return self._client.delete_item(TableName=table_name, Key=key)
