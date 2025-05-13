from dataclasses import dataclass

from quant_core.enums.platform import Platform
from quant_core.enums.prop_firm import PropFirm


@dataclass
class AccountDTO:
    """DTO for Account entity."""

    id: int
    uid: str
    platform: Platform
    prop_firm: PropFirm
    friendly_name: str
    secret_name: str
    enabled: bool
