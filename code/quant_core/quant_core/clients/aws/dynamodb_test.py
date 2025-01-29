import boto3
from moto import mock_aws

from quant_core.clients.aws.dynamodb import DynamoDBClient


@mock_aws
class TestDynamoDBClient:
    def setup_method(self, _) -> None:
        self.dynamodb_resource = boto3.resource("dynamodb", region_name="eu-west-1")

        self.table_name = "test_table"
        self.table = self.dynamodb_resource.create_table(
            TableName=self.table_name,
            KeySchema=[{"AttributeName": "test_key", "KeyType": "HASH"}],
            AttributeDefinitions=[{"AttributeName": "test_key", "AttributeType": "S"}],
            BillingMode="PAY_PER_REQUEST",
        )

        self.table.wait_until_exists()

        self._client = DynamoDBClient()

    def teardown_method(self, _) -> None:
        self.table.delete()
        self.table.wait_until_not_exists()

    def test_put_item_and_get_item(self) -> None:
        put_response = self._client.put_item(
            table_name=self.table_name, item={"test_key": {"S": "test_value"}, "another_field": {"S": "hello_world"}}
        )

        assert put_response["ResponseMetadata"]["HTTPStatusCode"] == 200

        get_response = self._client.get_item(table_name=self.table_name, key={"test_key": {"S": "test_value"}})

        assert "Item" in get_response
        assert get_response["Item"]["test_key"]["S"] == "test_value"
        assert get_response["Item"]["another_field"]["S"] == "hello_world"

    def test_delete_item(self) -> None:
        self._client.put_item(
            table_name=self.table_name, item={"test_key": {"S": "to_delete"}, "temp_data": {"S": "some_temp_value"}}
        )

        delete_response = self._client.delete_item(table_name=self.table_name, key={"test_key": {"S": "to_delete"}})

        assert delete_response["ResponseMetadata"]["HTTPStatusCode"] == 200

        get_response = self._client.get_item(table_name=self.table_name, key={"test_key": {"S": "to_delete"}})
        assert "Item" not in get_response  # Should be no item found


def test_instantiate_dynamodb_client():
    client = DynamoDBClient()

    assert client is not None
