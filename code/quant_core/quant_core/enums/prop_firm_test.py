import os

import pytest

from quant_core.enums.prop_firm import PropFirm


class TestPropFirm:
    @pytest.mark.parametrize(
        "prop_firm",
        list(PropFirm),
    )
    def test_get_company_logo(self, prop_firm) -> None:
        logo_path = PropFirm(prop_firm).get_company_logo()

        assert os.path.exists(logo_path), f"Logo path does not exist: {logo_path}"
        assert logo_path.endswith(".png"), f"Logo path is not a PNG file: {logo_path}"
