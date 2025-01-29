from typing import Optional, List

import boto3

from quant_core.entities.active_order import ActiveOrder
from quant_core.settings.configuration import Configuration


class ActiveOrderStore:
    def __init__(self) -> None:
        self._client = boto3.client("dynamodb")
        self._active_order_table = f"active-order-items-{Configuration().environment.value.lower()}"
        self._active_orders = {}

    def upload_to_dynamodb(self, active_order: ActiveOrder) -> None:
        self._client.put_item(
            TableName=self._active_order_table,
            Item=active_order.to_dynamodb(),
        )

    def download_from_dynamodb(self) -> None:
        self._active_orders.clear()
        response = self._client.scan(TableName=self._active_order_table)
        for item in response["Items"]:
            active_order = ActiveOrder.from_dynamodb(item)
            self._active_orders[active_order.order_id] = active_order

    def delete_from_dynamodb(self, order_id: str) -> None:
        self._client.delete_item(
            TableName=self._active_order_table,
            Key={"order_id": {"S": order_id}},
        )

    def list(self) -> List[ActiveOrder]:
        return list(self._active_orders.values())

    def save(self, active_order: ActiveOrder) -> None:
        self._active_orders[active_order.order_id] = active_order

    def get(self, order_id: str) -> Optional[ActiveOrder]:
        return self._active_orders.get(order_id)

    def delete(self, order_id: str) -> None:
        self._active_orders.pop(order_id, None)
