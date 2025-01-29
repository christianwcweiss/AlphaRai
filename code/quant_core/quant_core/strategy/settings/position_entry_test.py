import os.path

import pytest

from quant_core.enums.order_type import OrderType
from quant_core.strategy.settings.position_entry import StrategySettingsPositionEntry

_EXAMPLE_YAML = os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", "..", "strategies", "example_tv", "position_entry_settings.yaml")


class TestStrategySettingsPositionEntry:
    pytest.mark.skipif(not os.path.exists(_EXAMPLE_YAML), reason="Example YAML file not found.")

    def test_load_from_yaml(self) -> None:
        settings = StrategySettingsPositionEntry.from_yaml(_EXAMPLE_YAML)

        assert settings.mode is OrderType.LIMIT

