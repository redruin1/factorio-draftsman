# test_electric_energy_interface.py
# -*- encoding: utf-8 -*-

from __future__ import unicode_literals

from draftsman.entity import (
    ElectricEnergyInterface,
    electric_energy_interfaces,
    Container,
)
from draftsman.error import InvalidEntityError
from draftsman.warning import DraftsmanWarning

from collections.abc import Hashable
import sys
import pytest

if sys.version_info >= (3, 3):  # pragma: no coverage
    import unittest
else:  # pragma: no coverage
    import unittest2 as unittest


class ElectricEnergyInterfaceTesting(unittest.TestCase):
    def test_contstructor_init(self):
        interface = ElectricEnergyInterface(
            "electric-energy-interface",
            buffer_size=10000,
            power_production=10000,
            power_usage=0,
        )
        assert interface.to_dict() == {
            "name": "electric-energy-interface",
            "position": {"x": 1.0, "y": 1.0},
            "buffer_size": 10000,
            "power_production": 10000,
            "power_usage": 0,
        }

        with pytest.warns(DraftsmanWarning):
            ElectricEnergyInterface(unused_keyword="whatever")

        with pytest.raises(InvalidEntityError):
            ElectricEnergyInterface("this is not an electric energy interface")

    def test_set_buffer_size(self):
        interface = ElectricEnergyInterface()
        interface.buffer_size = 100
        assert interface.buffer_size == 100
        interface.buffer_size = None
        assert interface.buffer_size == None
        with pytest.raises(TypeError):
            interface.buffer_size = "incorrect"

    def test_set_power_production(self):
        interface = ElectricEnergyInterface()
        interface.power_production = 100
        assert interface.power_production == 100
        interface.power_production = None
        assert interface.power_production == None
        with pytest.raises(TypeError):
            interface.power_production = "incorrect"

    def test_set_power_usage(self):
        interface = ElectricEnergyInterface()
        interface.power_usage = 100
        assert interface.power_usage == 100
        interface.power_usage = None
        assert interface.power_usage == None
        with pytest.raises(TypeError):
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

        interface2 = InvalidEntityError()
        assert not interface1.mergable_with(interface2)

    def test_merge(self):
        interface1 = ElectricEnergyInterface(
            "electric-energy-interface", buffer_size=100
        )
        interface2 = ElectricEnergyInterface(
            "electric-energy-interface",
            tags={"some": "stuff"},
            power_production=10000,
            power_usage=100,
        )

        interface1.merge(interface2)
        del interface2

        assert interface1.buffer_size == None
        assert interface1.power_production == 10000
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
