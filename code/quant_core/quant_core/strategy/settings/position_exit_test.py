import os.path

import pytest

from quant_core.enums.strategy import ExitCalculationMode
from quant_core.strategy.settings.position_exit import StrategySettingsPositionExit

_EXAMPLE_YAML = os.path.join(
    os.path.dirname(__file__), "..", "..", "..", "..", "..", "strategies", "example_tv", "position_exit_settings.yaml"
)


class TestStrategySettingsPositionExit:
    pytest.mark.skipif(not os.path.exists(_EXAMPLE_YAML), reason="Example YAML file not found.")

    def test_load_from_yaml(self) -> None:
        settings = StrategySettingsPositionExit.from_yaml(_EXAMPLE_YAML)

        assert settings.mode is ExitCalculationMode.ATR
        assert settings.value == 14
        assert settings.strong_sell_modifier == 1.5
        assert settings.sell_modifier == 1.0
        assert settings.buy_modifier == 1.0
        assert settings.strong_buy_modifier == 1.5
