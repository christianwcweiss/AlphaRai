import os
from enum import Enum


class PropFirm(Enum):
    """Prop Firm Enum to represent different proprietary trading firms."""

    FTMO = "FTMO"
    FUNDING_PIPS = "Funding Pips"
    THE_5_ERS = "5%ers"
    UNKNOWN = "unknown"

    def get_company_logo(self) -> str:
        """Get the path to the company logo image based on the prop firm."""
        images_path = os.path.join(
            os.path.dirname(__file__),
            "..",
            "..",
            "..",
            "assets",
            "images",
        )

        if self is PropFirm.FTMO:
            return os.path.join(images_path, "ftmo_logo.png")
        if self is PropFirm.FUNDING_PIPS:
            return os.path.join(images_path, "funding_pips_logo.png")
        if self is PropFirm.THE_5_ERS:
            return os.path.join(images_path, "5%ers_logo.png")
        if self is PropFirm.UNKNOWN:
            return os.path.join(images_path, "unknown_logo.png")

        raise ValueError(f"Unknown PropFirm: {self.value}")
