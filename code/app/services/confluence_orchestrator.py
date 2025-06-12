from typing import List

from entities.trade_details import TradeDetails
from models.main.confluence_config import ConfluenceConfig


class ConfluenceOrchestrator:

    def __init__(self, confluence_configs: List[ConfluenceConfig], trade: TradeDetails) -> None:
        self._confluence_configs = confluence_configs
        self._trade = trade

    def get_confluence_modifier(self) -> float:
        return 1.0
