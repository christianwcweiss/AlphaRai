import os
from functools import lru_cache


@lru_cache(1)
class Configuration:  # type: ignore  # pylint: disable=too-few-public-methods
    """Configuration class for the Quant Core application."""

    def __init__(self) -> None:
        self._sns_topic_arn = os.environ.get("SNS_TOPIC_ARN", "not-set")  # for now only needed for the lambda.

    @property
    def sns_topic_arn(self) -> str:
        """Returns the SNS topic ARN for notifications."""
        return self._sns_topic_arn
