# test_furnace.py

from draftsman.constants import Direction, Inventory
from draftsman.entity import Furnace, furnaces, Container
from draftsman.error import DataFormatError
from draftsman.warning import (
    ModuleCapacityWarning,
    ModuleNotAllowedWarning,
    ItemCapacityWarning,
    ItemLimitationWarning,
    FuelCapacityWarning,
    FuelLimitationWarning,
    UnknownEntityWarning,
    UnknownItemWarning,
    UnknownKeywordWarning,
)
from draftsman.signatures import (
    AttrsItemRequest,
    AttrsItemID,
    AttrsItemSpecification,
    AttrsInventoryLocation,
)

from collections.abc import Hashable
import pytest


@pytest.fixture
def valid_furnace():
    if len(furnaces) == 0:
        return None
    return Furnace(
        "electric-furnace",
        id="test",
        quality="uncommon",
        direction=Direction.EAST,
        tile_position=(1, 1),
        item_requests=[
            AttrsItemRequest(
                id=AttrsItemID(name="speed-module-3"),
                items=AttrsItemSpecification(
                    in_inventory=[
                        AttrsInventoryLocation(
                            inventory=Inventory.furnace_modules, stack=0, count=1
                        ),
                        AttrsInventoryLocation(
                            inventory=Inventory.furnace_modules, stack=1, count=1
                        ),
                    ]
                ),
            )
        ],
        tags={"blah": "blah"},
    )


class TestFurnace:
    def test_constructor_init(self):
        furnace = Furnace("stone-furnace")

        # Warnings
        with pytest.warns(UnknownEntityWarning):
            Furnace("not a furnace").validate().reissue_all()

        # Errors

    def test_json_schema(self):
        assert Furnace.json_schema(version=(1, 0)) == {
            "$id": "urn:factorio:entity:furnace",
            "$schema": "https://json-schema.org/draft/2020-12/schema",
            "type": "object",
            "properties": {
                "entity_number": {"$ref": "urn:uint64"},
                "name": {"type": "string"},
                "position": {"$ref": "urn:factorio:position"},
                "direction": {"enum": list(range(8)), "default": 0},
                "items": {
                    "type": "object",
                    "description": "A dictionary of item requests, where each key is "
                    "the name of an item and the value is the count of that item to "
                    "request. Items always go to the default inventory of that object "
                    "(if possible) in the order in which Factorio traverses them.",
                },
                "tags": {"type": "object"},
            },
            "required": ["entity_number", "name", "position"],
        }
        assert Furnace.json_schema(version=(2, 0)) == {
            "$id": "urn:factorio:entity:furnace",
            "$schema": "https://json-schema.org/draft/2020-12/schema",
            "type": "object",
            "properties": {
                "entity_number": {"$ref": "urn:uint64"},
                "name": {"type": "string"},
                "position": {"$ref": "urn:factorio:position"},
                "quality": {"$ref": "urn:factorio:quality-name"},
                "direction": {"enum": list(range(16)), "default": 0},
                "items": {
                    "type": "array",
                    "items": {"$ref": "urn:factorio:item-request"},
                    "description": "A list of item requests objects, which contain "
                    "the item name, it's quality, the amount to request, as well as "
                    "exactly what inventories to request to and where inside those "
                    "inventories.",
                },
                "control_behavior": {
                    "type": "object",
                    "properties": {
                        "circuit_enabled": {"type": "boolean", "default": "false"},
                        "circuit_condition": {"$ref": "urn:factorio:simple-condition"},
                        "connect_to_logistic_network": {
                            "type": "boolean",
                            "default": "false",
                        },
                        "logistic_condition": {"$ref": "urn:factorio:simple-condition"},
                        "set_recipe": {"type": "boolean", "default": "false"},
                        "read_contents": {"type": "boolean", "default": "false"},
                        "include_in_crafting": {"type": "boolean", "default": "true"},
                        "read_recipe_finished": {"type": "boolean", "default": "false"},
                        "recipe_finished_signal": {
                            "anyOf": [
                                {"$ref": "urn:factorio:signal-id"},
                                {"type": "null"},
                            ]
                        },
                        "read_working": {"type": "boolean", "default": "false"},
                        "working_signal": {
                            "anyOf": [
                                {"$ref": "urn:factorio:signal-id"},
                                {"type": "null"},
                            ]
                        },
                    },
                    "description": "Entity-specific structure which holds keys related to configuring how this entity acts.",
                },
                "tags": {"type": "object"},
            },
            "required": ["entity_number", "name", "position"],
        }

    def test_allowed_effects(self):
        furnace = Furnace("stone-furnace")
        assert furnace.allowed_effects == {"consumption", "speed", "pollution"}
        furnace = Furnace("electric-furnace")
        assert furnace.allowed_effects == {
            "speed",
            "productivity",
            "quality",
            "pollution",
            "consumption",
        }

        with pytest.warns(UnknownEntityWarning):
            furnace = Furnace("unknown-furance")
        assert furnace.allowed_effects == None

    def test_allowed_input_ingredients(self):
        furnace = Furnace("stone-furnace")
        assert furnace.allowed_input_ingredients == {
            "iron-plate",
            "stone",
            "iron-ore",
            "lithium",
            "copper-ore",
        }
        furnace = Furnace("electric-furnace")
        assert furnace.allowed_input_ingredients == {
            "iron-plate",
            "stone",
            "iron-ore",
            "lithium",
            "copper-ore",
        }

        with pytest.warns(UnknownEntityWarning):
            furnace = Furnace("unknown-furance")
        assert furnace.allowed_input_ingredients == None

    def test_fuel_input_size(self):
        furnace = Furnace("stone-furnace")
        assert furnace.energy_source["type"] == "burner"
        assert furnace.fuel_input_size == 1
        assert furnace.fuel_output_size == 0

        furnace = Furnace("electric-furnace")
        assert furnace.energy_source["type"] == "electric"
        assert furnace.fuel_input_size == 0
        assert furnace.fuel_output_size == 0

        furnace = Furnace("unknown-furnace", validate_assignment="none")
        assert furnace.energy_source is None
        assert furnace.fuel_input_size is None
        assert furnace.fuel_output_size is None

    def test_set_item_request(self):
        furnace = Furnace("stone-furnace")
        assert furnace.allowed_modules == {
            "efficiency-module",
            "efficiency-module-2",
            "efficiency-module-3",
            "speed-module",
            "speed-module-2",
            "speed-module-3",
        }
        assert furnace.total_module_slots == 0

        # # No slots on stone furnace for modules
        # with pytest.warns(ModuleCapacityWarning):
        #     furnace.set_item_request("speed-module", 2)
        # assert furnace.items == {"speed-module": 2}

        # # Too much fuel
        # with pytest.warns(FuelCapacityWarning):
        #     furnace.items = {"coal": 100}
        # assert furnace.items == {"coal": 100}

        # # Fuel, but not used
        # with pytest.warns(FuelLimitationWarning):
        #     furnace.items = {"uranium-fuel-cell": 1}
        # assert furnace.items == {"uranium-fuel-cell": 1}

        furnace = Furnace("electric-furnace")

        # Test setting to None removes
        furnace.set_item_request("coal", 50, inventory=Inventory.fuel)
        furnace.set_item_request("coal", None)
        assert furnace.item_requests == []

        # Test resetting count of existing request
        furnace.set_item_request(
            "coal", 25, inventory=Inventory.fuel, quality="legendary"
        )
        furnace.set_item_request(
            "coal", 50, inventory=Inventory.fuel, quality="legendary"
        )
        assert furnace.item_requests == [
            AttrsItemRequest(
                id=AttrsItemID(name="coal", quality="legendary"),
                items=AttrsItemSpecification(
                    in_inventory=[
                        AttrsInventoryLocation(
                            inventory=Inventory.fuel, stack=0, count=50
                        )
                    ]
                ),
            )
        ]

        # Test setting to None resets to empty list
        furnace.item_requests = None
        assert furnace.item_requests == []

    def test_mergable_with(self):
        furnace1 = Furnace("stone-furnace")
        furnace2 = Furnace("stone-furnace", tags={"some": "stuff"})

        assert furnace1.mergable_with(furnace1)

        assert furnace1.mergable_with(furnace2)
        assert furnace2.mergable_with(furnace1)

        furnace2.tile_position = (5, 5)
        assert not furnace1.mergable_with(furnace2)

        furnace2 = Furnace("electric-furnace")
        assert not furnace1.mergable_with(furnace2)

    def test_merge(self):
        furnace1 = Furnace("stone-furnace")
        furnace2 = Furnace("stone-furnace", tags={"some": "stuff"})

        furnace1.merge(furnace2)
        del furnace2

        assert furnace1.tags == {"some": "stuff"}

    def test_eq(self):
        furnace1 = Furnace("stone-furnace")
        furnace2 = Furnace("stone-furnace")

        assert furnace1 == furnace2

        furnace1.tags = {"some": "stuff"}

        assert furnace1 != furnace2

        container = Container()

        assert furnace1 != container
        assert furnace2 != container

        # hashable
        assert isinstance(furnace1, Hashable)
