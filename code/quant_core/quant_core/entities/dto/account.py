from dataclasses import dataclass
from typing import Optional
from quant_core.enums.platform import Platform
from quant_core.enums.prop_firm import PropFirm

@dataclass
class AccountDTO:
    """DTO for Account entity."""

    uid: str
    platform: Platform
    prop_firm: PropFirm
    friendly_name: str
    secret_name: Optional[str]
    mt5_username: Optional[str]
    mt5_password: Optional[str]
    mt5_server: Optional[str]
    enabled: bool
