from quant_core.metrics.account_growth.absolute.growth import AccountGrowthAbsoluteOverTime
from quant_dev.builder import Builder


class TestAccountGrowthAbsoluteOverTime:
    def test_calculation(self) -> None:
        data_frame = Builder.get_trade_history()

        result_data_frame = AccountGrowthAbsoluteOverTime().calculate(data_frame=data_frame)

        assert result_data_frame is not None