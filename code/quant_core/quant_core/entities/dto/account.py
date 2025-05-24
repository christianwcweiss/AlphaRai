from dataclasses import dataclass

from quant_core.enums.platform import Platform


@dataclass
class AccountDTO:
    """DTO for Account entity."""

    id: int
    uid: str
    platform: Platform
    friendly_name: str
    secret_name: str
    enabled: bool
