import os.path

import pytest

from quant_core.enums.strategy import CalculationMode
from quant_core.strategy.settings.position_size import StrategySettingsPositionSize

_EXAMPLE_YAML = os.path.join(
    os.path.dirname(__file__), "..", "..", "..", "..", "..", "strategies", "example_tv", "position_size_settings.yaml"
)


class TestStrategySettingsPositionSize:
    pytest.mark.skipif(not os.path.exists(_EXAMPLE_YAML), reason="Example YAML file not found.")

    def test_load_from_yaml(self) -> None:
        settings = StrategySettingsPositionSize.from_yaml(_EXAMPLE_YAML)

        assert settings.mode is CalculationMode.FIXED
        assert settings.value == 0.1
