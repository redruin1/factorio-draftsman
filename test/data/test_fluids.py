# test_fluids.py

from draftsman.data import fluids
from draftsman.error import InvalidFluidError

import pytest


class TestFluidData:
    def test_add_fluid(self):
        fluids.add_fluid("custom-fluid")
        assert fluids.raw["custom-fluid"] == {
            "name": "custom-fluid",
            "order": "",
            "default_temperature": 25,
            "type": "fluid",
        }

    def test_get_temperature_range(self):
        assert fluids.get_temperature_range("water") == (15, 100)
        assert fluids.get_temperature_range("steam") == (15, 5000)
        assert fluids.get_temperature_range("petroleum-gas") == (25, 25)

        with pytest.raises(InvalidFluidError):
            fluids.get_temperature_range("incorrect")
