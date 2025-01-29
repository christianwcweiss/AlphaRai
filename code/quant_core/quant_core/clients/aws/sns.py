import boto3


class SNSClient:
    def __init__(self) -> None:
        self._client = boto3.client("sns")

    def publish(self, topic_arn: str, message: str) -> None:
        self._client.publish(TopicArn=topic_arn, Message=message)
