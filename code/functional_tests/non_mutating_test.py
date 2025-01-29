from time import sleep

import pytest

from quant_core.clients.ig.ig_api import IGApi, IGApiGetPricesBody
from quant_core.entities.chart_data import ChartData
from quant_core.entities.ig.epic import Epic
from quant_core.enums.time_period import TimePeriod


class TestNonMutating:
    @pytest.mark.parametrize("epic", EPIC_LIST)
    @pytest.mark.parametrize("time_period", list(TimePeriod))
    def test_all_epics_are_correct_and_successful(self, epic: Epic, time_period: TimePeriod) -> None:
        ig_api = IGApi()
        prices_body = IGApiGetPricesBody(
            epic=epic.epic_id, resolution=time_period.to_ig_period(), max_items=500, page_size=500
        )

        prices = ig_api.get_prices(prices_body)
        chart_data = ChartData.from_ig_data(prices)

        assert len(prices) == 500
        assert len(chart_data.data_frame) == 500

        sleep(5)
