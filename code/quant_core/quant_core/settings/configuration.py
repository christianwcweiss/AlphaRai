import os
from functools import lru_cache
from typing import Optional

from quant_core.enums.environment import Environment


@lru_cache(1)
class Configuration:
    def __init__(self) -> None:
        self._environment = Environment(os.environ["ENVIRONMENT"])
        self._sns_topic_arn = os.environ.get("SNS_TOPIC_ARN")

    @property
    def environment(self) -> Environment:
        return self._environment

    @property
    def sns_topic_arn(self) -> Optional[str]:
        return self._sns_topic_arn
