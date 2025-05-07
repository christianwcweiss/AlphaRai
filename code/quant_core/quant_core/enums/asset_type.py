from enum import Enum


class AssetType(Enum):
    UNKNOWN = "unknown"
    STOCK = "STOCK"
    CRYPTO = "CRYPTO"
    FOREX = "FOREX"
    INDICES = "INDICES"
