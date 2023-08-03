# test_assembling_machine.py
# -*- encoding: utf-8 -*-

from __future__ import unicode_literals

from draftsman.constants import Direction
from draftsman.entity import AssemblingMachine, assembling_machines
from draftsman.error import InvalidEntityError, InvalidRecipeError, InvalidItemError
from draftsman.warning import (
    DraftsmanWarning,
    ModuleLimitationWarning,
    ItemLimitationWarning,
)

import warnings

import sys
import pytest

if sys.version_info >= (3, 3):  # pragma: no coverage
    import unittest
else:  # pragma: no coverage
    import unittest2 as unittest


class AssemblingMachineTesting(unittest.TestCase):
    def test_constructor_init(self):
        assembler = AssemblingMachine("assembling-machine-1", recipe="iron-gear-wheel")
        assert assembler.to_dict() == {
            "name": "assembling-machine-1",
            "position": {"x": 1.5, "y": 1.5},
            "recipe": "iron-gear-wheel",
        }
        assembler.recipe = None
        assert assembler.to_dict() == {
            "name": "assembling-machine-1",
            "position": {"x": 1.5, "y": 1.5},
        }

        # Warnings
        with pytest.warns(DraftsmanWarning):
            AssemblingMachine(unused_keyword="whatever")

        # Errors
        with pytest.raises(InvalidEntityError):
            AssemblingMachine("not an assembling machine")
        with pytest.raises(InvalidRecipeError):
            AssemblingMachine(recipe="invalid")

    def test_set_recipe(self):
        machine = AssemblingMachine("assembling-machine-3")
        machine.set_item_request("productivity-module-3", 2)

        with warnings.catch_warnings(record=True) as w:
            machine.recipe = "iron-gear-wheel"
            assert len(w) == 0

        with pytest.warns(ModuleLimitationWarning):
            machine.recipe = "wooden-chest"

        machine.set_item_request("speed-module-3", 2)
        with pytest.warns(ModuleLimitationWarning):
            machine.recipe = "iron-chest"

    def test_set_item_request(self):
        machine = AssemblingMachine("assembling-machine-3")
        machine.recipe = "wooden-chest"
        with pytest.warns(ModuleLimitationWarning):
            machine.set_item_request("productivity-module-3", 2)

        machine.set_item_request("wood", 20)
        assert machine.items == {"productivity-module-3": 2, "wood": 20}

        machine.recipe = None
        machine.set_item_requests(None)

        machine.set_item_request("iron-plate", 100)
        assert machine.items == {"iron-plate": 100}
        machine.recipe = "iron-gear-wheel"
        # Raise warning when setting recipe that conficts with request
        with pytest.warns(ItemLimitationWarning):
            machine.recipe = "wooden-chest"

        with pytest.warns(ItemLimitationWarning):
            machine.set_item_request("copper-cable", 100)

        machine.recipe = "electronic-circuit"

        # Errors
        with pytest.raises(TypeError):
            machine.set_item_request(None, "nonsense")
        with pytest.raises(InvalidItemError):
            machine.set_item_request("incorrect", 100)
        with pytest.raises(TypeError):
            machine.set_item_request("speed-module-2", "nonsense")
        with pytest.raises(ValueError):
            machine.set_item_request("speed-module-2", -1)

    def test_mergable_with(self):
        machine1 = AssemblingMachine("assembling-machine-1")
        machine2 = AssemblingMachine("assembling-machine-1")

        assert machine1.mergable_with(machine2)
        assert machine2.mergable_with(machine1)

        machine2 = AssemblingMachine("assembling-machine-1", tags={"some": "stuff"})
        assert machine1.mergable_with(machine2)

        machine2.recipe = "copper-cable"
        machine2.set_item_request("copper-plate", 100)
        assert machine1.mergable_with(machine2)

        machine2 = AssemblingMachine("assembling-machine-2")
        assert not machine1.mergable_with(machine2)

        machine2 = AssemblingMachine("assembling-machine-1", tile_position=(1, 1))
        assert not machine1.mergable_with(machine2)

        machine2 = AssemblingMachine("assembling-machine-1", direction=Direction.EAST)
        assert not machine1.mergable_with(machine2)

    def test_merge(self):
        machine1 = AssemblingMachine("assembling-machine-1")
        machine2 = AssemblingMachine("assembling-machine-1", tags={"some": "stuff"})
        machine2.recipe = "copper-cable"
        machine2.set_item_request("copper-plate", 100)

        machine1.merge(machine2)
        del machine2

        assert machine1.tags == {"some": "stuff"}
        assert machine1.recipe == "copper-cable"
        assert machine1.items == {"copper-plate": 100}
