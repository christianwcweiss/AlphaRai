import os
from functools import lru_cache

from quant_core.enums.environment import Environment


@lru_cache(1)
class Configuration:
    """Configuration class for the Quant Core application."""

    def __init__(self) -> None:
        self._environment = Environment(os.environ["ENVIRONMENT"])
        self._sns_topic_arn = os.environ.get("SNS_TOPIC_ARN", "not-set")  # for now only needed for the lambda.

    @property
    def environment(self) -> Environment:
        """Returns the current environment."""
        return self._environment

    @property
    def sns_topic_arn(self) -> str:
        """Returns the SNS topic ARN for notifications."""
        return self._sns_topic_arn
