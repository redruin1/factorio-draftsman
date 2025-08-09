# test_heat_interface.py

from draftsman.constants import ValidationMode
from draftsman.entity import HeatInterface, heat_interfaces, Container
from draftsman.error import DataFormatError
import draftsman.validators
from draftsman.warning import (
    UnknownEntityWarning,
    UnknownKeywordWarning,
    TemperatureRangeWarning,
)

from collections.abc import Hashable
import pytest


@pytest.fixture
def valid_heat_interface():
    return HeatInterface(
        "heat-interface",
        id="test",
        quality="uncommon",
        tile_position=(1, 1),
        temperature=100,
        mode="at-most",
        tags={"blah": "blah"},
    )


class TestHeatInterface:
    def test_constructor_init(self):
        interface = HeatInterface(temperature=10, mode="at-most")
        assert interface.to_dict() == {
            "name": "heat-interface",
            "position": {"x": 0.5, "y": 0.5},
            "temperature": 10,
            "mode": "at-most",
        }

        # Warnings
        with pytest.warns(UnknownEntityWarning):
            HeatInterface("this is not a heat interface").validate().reissue_all()

        with pytest.warns(TemperatureRangeWarning):
            HeatInterface(temperature=100_000).validate(mode="pedantic").reissue_all()

        # Errors
        with pytest.raises(DataFormatError):
            HeatInterface(temperature="incorrect").validate().reissue_all()

    def test_set_temperature(self):
        interface = HeatInterface()
        assert interface.temperature == 0.0

        interface.temperature = 100
        assert interface.temperature == 100

        # No warnings on strict
        interface.temperature = -1000
        assert interface.temperature == -1000

        # Single warning on pedantic
        with draftsman.validators.set_mode(ValidationMode.PEDANTIC):
            interface.temperature = 100
            assert interface.temperature == 100
            with pytest.warns(TemperatureRangeWarning):
                interface.temperature = -1000
            assert interface.temperature == -1000

        # Errors
        with pytest.raises(DataFormatError):
            interface.temperature = "incorrect"

    def test_set_mode(self):
        interface = HeatInterface()
        assert interface.mode == "at-least"

        interface.mode = "exactly"
        assert interface.mode == "exactly"

        with pytest.raises(DataFormatError):
            interface.mode = "incorrect"

    def test_mergable_with(self):
        interface1 = HeatInterface("heat-interface")
        interface2 = HeatInterface("heat-interface", mode="at-most", temperature=100)

        assert interface1.mergable_with(interface1)

        assert interface1.mergable_with(interface2)
        assert interface2.mergable_with(interface1)

        interface2.tile_position = (10, 10)
        assert not interface1.mergable_with(interface2)

    def test_merge(self):
        interface1 = HeatInterface("heat-interface")
        interface2 = HeatInterface(
            "heat-interface", mode="at-most", temperature=100, tags={"some": "stuff"}
        )

        interface1.merge(interface2)
        del interface2

        assert interface1.temperature == 100
        assert interface1.mode == "at-most"
        assert interface1.tags == {"some": "stuff"}

    def test_eq(self):
        interface1 = HeatInterface("heat-interface")
        interface2 = HeatInterface("heat-interface")

        assert interface1 == interface2

        interface1.tags = {"some": "stuff"}

        assert interface1 != interface2

        container = Container()

        assert interface1 != container
        assert interface2 != container

        # hashable
        assert isinstance(interface1, Hashable)
