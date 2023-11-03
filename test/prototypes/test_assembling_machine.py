# test_assembling_machine.py

from draftsman.constants import Direction
from draftsman.entity import AssemblingMachine, assembling_machines, Container
from draftsman.error import InvalidEntityError, InvalidRecipeError, InvalidItemError, DataFormatError
from draftsman.warning import (
    ModuleCapacityWarning,
    ModuleLimitationWarning,
    ItemLimitationWarning,
    UnknownEntityWarning,
    UnknownKeywordWarning,
    UnknownRecipeWarning,
)

import warnings

from collections.abc import Hashable
import pytest


class TestAssemblingMachine:
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
        with pytest.warns(UnknownKeywordWarning):
            AssemblingMachine(unused_keyword="whatever")
        with pytest.warns(UnknownRecipeWarning):
            AssemblingMachine(recipe="incorrect")
        with pytest.warns(UnknownEntityWarning):
            AssemblingMachine("not an assembling machine")

        # Errors
        with pytest.raises(DataFormatError):
            AssemblingMachine(recipe=100)

    def test_set_recipe(self):
        machine = AssemblingMachine("assembling-machine-3")
        assert machine.allowed_modules == {
            'speed-module',
            'speed-module-2',
            'speed-module-3',
            'effectivity-module',
            'effectivity-module-2',
            'effectivity-module-3',
            'productivity-module',
            'productivity-module-2',
            'productivity-module-3'
        }
        machine.set_item_request("productivity-module-3", 2)
        
        machine.recipe = "iron-gear-wheel"
        assert machine.recipe == "iron-gear-wheel"
        assert machine.allowed_modules == {
            'speed-module',
            'speed-module-2',
            'speed-module-3',
            'effectivity-module',
            'effectivity-module-2',
            'effectivity-module-3',
            'productivity-module',
            'productivity-module-2',
            'productivity-module-3'
        }

        with pytest.warns(ItemLimitationWarning):
            machine.recipe = "wooden-chest"
        assert machine.allowed_modules == {
            'speed-module',
            'speed-module-2',
            'speed-module-3',
            'effectivity-module',
            'effectivity-module-2',
            'effectivity-module-3',
        }

        machine.items = None
        with pytest.warns(ModuleCapacityWarning):
            machine.set_item_request("speed-module-3", 10)
        # with pytest.warns(ModuleLimitationWarning):
        #     machine.recipe = "iron-chest"

    def test_set_item_request(self):
        machine = AssemblingMachine("assembling-machine-3")
        machine.recipe = "wooden-chest"
        with pytest.warns(ModuleLimitationWarning):
            machine.set_item_request("productivity-module-3", 2)

        machine.items = None # TODO: should be able to remove this
        machine.set_item_request("wood", 20) # because this ideally shouldn't raise a warning
        assert machine.items == {"wood": 20} # {"productivity-module-3": 2, "wood": 20}

        machine.recipe = None
        machine.items = None

        print(machine.allowed_items)
        machine.set_item_request("iron-plate", 100)
        assert machine.items == {"iron-plate": 100}
        machine.recipe = "iron-gear-wheel"
        assert machine.allowed_input_ingredients == {"iron-plate"}
        # Raise warning when setting recipe that conficts with request
        with pytest.warns(ItemLimitationWarning):
            machine.recipe = "wooden-chest"

        with pytest.warns(ItemLimitationWarning):
            machine.set_item_request("copper-cable", 100)

        machine.recipe = "electronic-circuit"

        # Errors
        with pytest.raises(TypeError):
            machine.set_item_request(None, "nonsense")
        # with pytest.raises(InvalidItemError): # TODO
        #     machine.set_item_request("incorrect", 100)
        with pytest.raises(TypeError):
            machine.set_item_request("speed-module-2", "nonsense")
        # with pytest.raises(ValueError): # TODO
        #     machine.set_item_request("speed-module-2", -1)

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

    def test_eq(self):
        machine1 = AssemblingMachine("assembling-machine-1")
        machine2 = AssemblingMachine("assembling-machine-1")

        assert machine1 == machine2

        machine1.recipe = "iron-gear-wheel"

        assert machine1 != machine2

        container = Container()

        assert machine1 != container
        assert machine2 != container

        # hashable
        assert isinstance(machine1, Hashable)
