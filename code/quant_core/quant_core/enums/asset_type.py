from enum import Enum


class AssetType(Enum):
    """Asset types for financial instruments."""

    UNKNOWN = "UNKNOWN"
    STOCK = "STOCK"
    CRYPTO = "CRYPTO"
    FOREX = "FOREX"
    INDICES = "INDICES"
    FUNDS = "FUNDS"
    COMMODITIES = "COMMODITIES"
