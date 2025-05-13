import boto3


class SNSClient:  # pylint: disable=too-few-public-methods
    """Helper class to send messages to AWS SNS topics."""

    def __init__(self) -> None:
        self._client = boto3.client("sns")

    def publish(self, topic_arn: str, message: str) -> None:
        """Publish a message to an SNS topic."""
        self._client.publish(TopicArn=topic_arn, Message=message)
