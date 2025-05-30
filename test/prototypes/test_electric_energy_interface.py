# test_electric_energy_interface.py

from draftsman.entity import (
    ElectricEnergyInterface,
    electric_energy_interfaces,
    Container,
)
from draftsman.error import DataFormatError
from draftsman.warning import UnknownEntityWarning, UnknownKeywordWarning

from collections.abc import Hashable
import pytest


@pytest.fixture
def valid_electric_energy_interface():
    if len(electric_energy_interfaces) == 0:
        return None
    return ElectricEnergyInterface(
        "electric-energy-interface",
        id="test",
        quality="uncommon",
        tile_position=(1, 1),
        buffer_size=1000,
        power_production=1000,
        power_usage=1000,
        tags={"blah": "blah"},
    )


class TestElectricEnergyInterface:
    def test_constructor_init(self):
        interface = ElectricEnergyInterface(
            "electric-energy-interface",
        )
        assert interface.to_dict() == {
            "name": "electric-energy-interface",
            "position": {"x": 1.0, "y": 1.0},
        }
        assert interface.to_dict(exclude_defaults=False) == {
            "name": "electric-energy-interface",
            "quality": "normal",
            "position": {"x": 1.0, "y": 1.0},
            "mirror": False,
            "buffer_size": 10000000000.0,
            "power_production": 8333333333.0,
            "power_usage": 0.0,
            "tags": {},
        }

        with pytest.warns(UnknownEntityWarning):
            ElectricEnergyInterface(
                "this is not an electric energy interface"
            ).validate().reissue_all()

    def test_set_buffer_size(self):
        interface = ElectricEnergyInterface("electric-energy-interface")
        assert interface.buffer_size == interface.default_buffer_size

        interface.buffer_size = 100
        assert interface.buffer_size == 100

        with pytest.raises(DataFormatError):
            interface.buffer_size = "incorrect"

    def test_set_power_production(self):
        interface = ElectricEnergyInterface("electric-energy-interface")
        assert interface.power_production == interface.default_power_production

        interface.power_production = 100
        assert interface.power_production == 100

        with pytest.raises(DataFormatError):
            interface.power_production = "incorrect"

    def test_set_power_usage(self):
        interface = ElectricEnergyInterface("electric-energy-interface")
        assert interface.power_usage == interface.default_power_usage

        interface.power_usage = 100
        assert interface.power_usage == 100

        with pytest.raises(DataFormatError):
            interface.power_usage = "incorrect"

    def test_mergable_with(self):
        interface1 = ElectricEnergyInterface("electric-energy-interface")
        interface2 = ElectricEnergyInterface(
            "electric-energy-interface",
            tags={"some": "stuff"},
            buffer_size=10000,
            power_production=10000,
            power_usage=100,
        )

        assert interface1.mergable_with(interface2)
        assert interface2.mergable_with(interface1)

        interface1.tile_position = (2, 2)
        assert not interface1.mergable_with(interface2)

        interface2 = DataFormatError()
        assert not interface1.mergable_with(interface2)

    def test_merge(self):
        interface1 = ElectricEnergyInterface(
            "electric-energy-interface", buffer_size=100
        )
        interface2 = ElectricEnergyInterface(
            "electric-energy-interface",
            tags={"some": "stuff"},
            power_production=10_000,
            power_usage=100,
        )

        interface1.merge(interface2)
        del interface2

        assert interface1.buffer_size == 10_000_000_000
        assert interface1.power_production == 10_000
        assert interface1.power_usage == 100
        assert interface1.tags == {"some": "stuff"}

    def test_eq(self):
        interface1 = ElectricEnergyInterface("electric-energy-interface")
        interface2 = ElectricEnergyInterface("electric-energy-interface")

        assert interface1 == interface2

        interface1.tags = {"some": "stuff"}

        assert interface1 != interface2

        container = Container()

        assert interface1 != container
        assert interface2 != container

        # hashable
        assert isinstance(interface1, Hashable)
