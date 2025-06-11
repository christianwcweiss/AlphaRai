from enum import Enum

from quant_core.confluences.adaptive_super_trend.ast_confluence import ConfluenceAdaptiveSuperTrendDirection
from quant_core.confluences.nadaraya_watson_envelope.nwe_envelope import ConfluenceNadarayaWatsonEnvelopePosition


class Confluence(Enum):
    """Enum for different confluence types."""

    ADAPTIVE_SUPER_TREND = ConfluenceAdaptiveSuperTrendDirection
    NADARAYA_WATSON_ENVELOPE = ConfluenceNadarayaWatsonEnvelopePosition
