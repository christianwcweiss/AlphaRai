import pytest

from components.molecules.toolbars.analytics_toolbar import analytics_bar_get_active_states
from quant_dev.builder import Builder


@pytest.mark.parametrize(
    "current_state,trigger_id,expected",
    [
        (True, "group-by-account-id", False),
        (False, "group-by-account-id", True),
        (True, "group-by-symbol", False),
        (False, "group-by-symbol", True),
        (True, "group-by-asset-type", False),
        (False, "group-by-asset-type", True),
        (True, "group-by-direction", False),
        (False, "group-by-direction", True),
        (True, "group-by-hour", False),
        (False, "group-by-hour", True),
        (True, "group-by-weekday", False),
        (False, "group-by-weekday", True),
    ],
)
def test_analytics_bar_group_by_toggle(
    current_state: bool,
    trigger_id: str,
    expected: bool,
) -> None:
    group_by_account_id = current_state if trigger_id == "group-by-account-id" else Builder.build_random_bool()
    group_by_symbol = current_state if trigger_id == "group-by-symbol" else Builder.build_random_bool()
    group_by_asset_type = current_state if trigger_id == "group-by-asset-type" else Builder.build_random_bool()
    group_by_direction = current_state if trigger_id == "group-by-direction" else Builder.build_random_bool()
    group_by_hour = current_state if trigger_id == "group-by-hour" else Builder.build_random_bool()
    group_by_weekday = current_state if trigger_id == "group-by-weekday" else Builder.build_random_bool()
    abs_active = Builder.build_random_bool()
    rel_active = Builder.build_random_bool()

    actual_result = analytics_bar_get_active_states(
        group_by_account_id=group_by_account_id,
        group_by_symbol=group_by_symbol,
        group_by_asset_type=group_by_asset_type,
        group_by_direction=group_by_direction,
        group_by_hour=group_by_hour,
        group_by_weekday=group_by_weekday,
        abs_active=abs_active,
        rel_active=rel_active,
        trigger_id=trigger_id,
    )

    (
        actual_group_by_account_id,
        actual_group_by_symbol,
        actual_group_by_asset_type,
        actual_group_by_direction,
        actual_group_by_hour,
        actual_group_by_weekday,
        _actual_abs_active,
        _actual_rel_active,
    ) = actual_result

    if trigger_id == "group-by-account-id":
        assert actual_group_by_account_id == expected
    else:
        assert actual_group_by_account_id == group_by_account_id

    if trigger_id == "group-by-symbol":
        assert actual_group_by_symbol == expected
    else:
        assert actual_group_by_symbol == group_by_symbol

    if trigger_id == "group-by-asset-type":
        assert actual_group_by_asset_type == expected
    else:
        assert actual_group_by_asset_type == group_by_asset_type

    if trigger_id == "group-by-direction":
        assert actual_group_by_direction == expected
    else:
        assert actual_group_by_direction == group_by_direction

    if trigger_id == "group-by-hour":
        assert actual_group_by_hour == expected
    else:
        assert actual_group_by_hour == group_by_hour

    if trigger_id == "group-by-weekday":
        assert actual_group_by_weekday == expected
    else:
        assert actual_group_by_weekday == group_by_weekday
