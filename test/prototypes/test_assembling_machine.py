# test_assembling_machine.py

from draftsman.constants import Direction, Inventory
from draftsman.entity import AssemblingMachine, assembling_machines, Container
from draftsman.error import (
    InvalidEntityError,
    InvalidRecipeError,
    InvalidItemError,
    DataFormatError,
)
from draftsman.signatures import AttrsItemRequest
from draftsman.warning import (
    ModuleCapacityWarning,
    ModuleLimitationWarning,
    ItemLimitationWarning,
    RecipeLimitationWarning,
    UnknownEntityWarning,
    UnknownItemWarning,
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
        with pytest.warns(UnknownRecipeWarning):
            AssemblingMachine(recipe="incorrect").validate().reissue_all()
        with pytest.warns(UnknownEntityWarning):
            AssemblingMachine("not an assembling machine").validate().reissue_all()

        # Errors
        with pytest.raises(DataFormatError):
            AssemblingMachine(recipe=100).validate().reissue_all()

    def test_power_and_circuit_flags(self):
        # TODO: what about different versions?
        for name in assembling_machines:
            assembling_machine = AssemblingMachine(name)
            assert assembling_machine.power_connectable == False
            assert assembling_machine.dual_power_connectable == False
            assert assembling_machine.circuit_connectable == True
            assert assembling_machine.dual_circuit_connectable == False

    def test_set_recipe(self):
        machine = AssemblingMachine("assembling-machine-3")
        assert machine.allowed_modules == {
            "speed-module",
            "speed-module-2",
            "speed-module-3",
            "efficiency-module",
            "efficiency-module-2",
            "efficiency-module-3",
            "productivity-module",
            "productivity-module-2",
            "productivity-module-3",
            "quality-module",
            "quality-module-2",
            "quality-module-3",
        }
        machine.set_item_request(
            "productivity-module-3",
            1,
            inventory=Inventory.assembling_machine_modules,
            slot=0,
        )
        machine.set_item_request(
            "productivity-module-3",
            1,
            inventory=Inventory.assembling_machine_modules,
            slot=1,
        )
        # TODO: make a `set_module_request()` method

        machine.recipe = "iron-gear-wheel"
        assert machine.recipe == "iron-gear-wheel"
        assert machine.allowed_modules == {
            "speed-module",
            "speed-module-2",
            "speed-module-3",
            "efficiency-module",
            "efficiency-module-2",
            "efficiency-module-3",
            "productivity-module",
            "productivity-module-2",
            "productivity-module-3",
            "quality-module",
            "quality-module-2",
            "quality-module-3",
        }

        with pytest.warns(ItemLimitationWarning):
            machine.recipe = "wooden-chest"
        assert machine.recipe == "wooden-chest"
        assert machine.allowed_modules == {
            "speed-module",
            "speed-module-2",
            "speed-module-3",
            "efficiency-module",
            "efficiency-module-2",
            "efficiency-module-3",
            "quality-module",
            "quality-module-2",
            "quality-module-3",
        }

        # machine.items = None
        # with pytest.warns(ModuleCapacityWarning):
        #     machine.set_item_request("speed-module-3", 10, inventory=Inventory.assembling_machine_modules)
        # with pytest.warns(ModuleLimitationWarning):
        #     machine.recipe = "iron-chest"

        # particular recipe not allowed in machine
        with pytest.warns(RecipeLimitationWarning):
            machine.recipe = "sulfur"
        assert machine.recipe == "sulfur"

        # Unknown recipe in an known machine
        machine = AssemblingMachine("assembling-machine-3")
        with pytest.warns(UnknownRecipeWarning):
            machine.recipe = "unknown"

        # Known recipe in an unknown machine
        with pytest.warns(UnknownEntityWarning):
            machine = AssemblingMachine("unknown")
        machine.recipe = "sulfur"

    def test_ingredient_items(self):
        machine = AssemblingMachine("assembling-machine-3")
        machine.recipe = "wooden-chest"
        assert machine.allowed_input_ingredients == {
            "wood"
        }
        machine.set_item_request("wood", 20, inventory=Inventory.assembling_machine_input)
        assert machine.ingredient_items == [
            AttrsItemRequest(
                id = {"name": "wood"},
                items={
                    "in_inventory": [
                        {
                            "inventory": 2,
                            "stack": 0,
                            "count": 20
                        }
                    ]
                }
            )
        ]

    # def test_set_item_request(self): # TODO: reimplement
    #     machine = AssemblingMachine("assembling-machine-3")
    #     machine.recipe = "wooden-chest"
    #     with pytest.warns(ModuleLimitationWarning):
    #         machine.set_item_request("productivity-module-3", 2)

    #     machine.items = None  # TODO: should be able to remove this
    #     machine.set_item_request(
    #         "wood", 20
    #     )  # because this ideally shouldn't raise a warning
    #     assert machine.items == {"wood": 20}  # {"productivity-module-3": 2, "wood": 20}

    #     # No warning when we omit recipe
    #     machine.recipe = None
    #     assert machine.recipe == None
    #     machine.items = {"productivity-module-3": 2, "productivity-module-2": 2}
    #     assert machine.items == {"productivity-module-3": 2, "productivity-module-2": 2}

    #     machine.recipe = None
    #     machine.items = None

    #     machine.set_item_request("iron-plate", 100)
    #     assert machine.items == {"iron-plate": 100}
    #     machine.recipe = "iron-gear-wheel"
    #     assert machine.allowed_input_ingredients == {"iron-plate"}
    #     # Raise warning when setting recipe that conficts with request
    #     with pytest.warns(ItemLimitationWarning):
    #         machine.recipe = "wooden-chest"

    #     with pytest.warns(ItemLimitationWarning):
    #         machine.set_item_request("copper-cable", 100)

    #     # Switching to the correct recipe raises no warnings as it fixes the issue
    #     machine.recipe = "electronic-circuit"

    #     # Errors
    #     machine.items = None
    #     with pytest.raises(DataFormatError):
    #         machine.set_item_request(None, "nonsense")
    #     with pytest.warns(UnknownItemWarning):
    #         machine.set_item_request("unknown", 100)
    #     with pytest.raises(DataFormatError):
    #         machine.set_item_request("speed-module-2", "nonsense")
    #     with pytest.raises(DataFormatError):
    #         machine.set_item_request("speed-module-2", -1)

    #     assert machine.items == {"unknown": 100}
    #     assert machine.module_slots_occupied == 0

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
        # machine2.set_item_request("copper-plate", 100)

        machine1.merge(machine2)
        del machine2

        assert machine1.tags == {"some": "stuff"}
        assert machine1.recipe == "copper-cable"

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
