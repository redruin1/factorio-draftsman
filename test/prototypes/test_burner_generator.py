# test_burner_generator.py

from draftsman.constants import Direction, Inventory
from draftsman.entity import BurnerGenerator, burner_generators, Container
from draftsman.error import InvalidEntityError
from draftsman.warning import (
    FuelCapacityWarning,
    ItemLimitationWarning,
    UnknownEntityWarning,
    UnknownKeywordWarning,
)

from collections.abc import Hashable
import pytest


@pytest.fixture
def valid_burner_generator():
    if len(burner_generators) == 0:
        return None
    return BurnerGenerator(
        "burner-generator",
        id="test",
        quality="uncommon",
        tile_position=(1, 1),
        direction=Direction.EAST,
        item_requests=[
            {
                "id": {"name": "coal"},
                "items": {
                    "in_inventory": [
                        {"inventory": Inventory.fuel, "stack": 0, "count": 50}
                    ]
                },
            }
        ],
        tags={"blah": "blah"},
    )


class TestBurnerGenerator:
    def test_contstructor_init(self):
        generator = BurnerGenerator("burner-generator")

        with pytest.warns(UnknownEntityWarning):
            BurnerGenerator("this is not a burner generator").validate().reissue_all()

    def test_json_schema(self):
        assert BurnerGenerator.json_schema(version=(1, 0)) == {
            "$id": "urn:factorio:entity:burner-generator",
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
                    "request. Items always go to the default inventory of that "
                    "object (if possible) in the order in which Factorio traverses "
                    "them.",
                },
                "tags": {"type": "object"},
            },
            "required": ["entity_number", "name", "position"],
        }
        assert BurnerGenerator.json_schema(version=(2, 0)) == {
            "$id": "urn:factorio:entity:burner-generator",
            "$schema": "https://json-schema.org/draft/2020-12/schema",
            "type": "object",
            "properties": {
                "entity_number": {"$ref": "urn:uint64"},
                "name": {"type": "string"},
                "position": {"$ref": "urn:factorio:position"},
                "direction": {"enum": list(range(16)), "default": 0},
                "quality": {"$ref": "urn:factorio:quality-name"},
                "items": {
                    "type": "array",
                    "items": {"$ref": "urn:factorio:item-request"},
                    "description": "A list of item requests objects, which contain "
                    "the item name, it's quality, the amount to request, as well as "
                    "exactly what inventories to request to and where inside those "
                    "inventories.",
                },
                "tags": {"type": "object"},
            },
            "required": ["entity_number", "name", "position"],
        }

    # def test_set_items(self): # TODO: reimplement
    #     generator = BurnerGenerator("burner-generator")
    #     assert generator.allowed_fuel_items == {
    #         "biter-egg",
    #         "carbon",
    #         "coal",
    #         "jelly",
    #         "jellynut",
    #         "jellynut-seed",
    #         "nuclear-fuel",
    #         "pentapod-egg",
    #         "rocket-fuel",
    #         "solid-fuel",
    #         "spoilage",
    #         "tree-seed",
    #         "wood",
    #         "yumako",
    #         "yumako-mash",
    #         "yumako-seed",
    #     }

    #     generator.set_item_request("coal", 50)
    #     assert generator.items == {"coal": 50}

    #     with pytest.warns(ItemLimitationWarning):
    #         generator.items = {"iron-plate": 1000}
    #     assert generator.items == {"iron-plate": 1000}

    #     with pytest.warns(FuelCapacityWarning):
    #         generator.set_item_request("coal", 200)
    #     assert generator.items == {"coal": 200, "iron-plate": 1000}

    #     generator.validate_assignment = "minimum"
    #     assert generator.validate_assignment == ValidationMode.MINIMUM

    #     generator.items = {"coal": 200, "iron-plate": 1000}
    #     assert generator.items == {"coal": 200, "iron-plate": 1000}

    #     # Ensure that validating without a custom context doesn't break it
    #     BurnerGenerator.Format.model_validate(generator._root)

    def test_mergable_with(self):
        generator1 = BurnerGenerator("burner-generator")
        generator2 = BurnerGenerator("burner-generator", tags={"some": "stuff"})

        assert generator1.mergable_with(generator2)
        assert generator2.mergable_with(generator1)

        generator2.tile_position = [-10, -10]
        assert not generator1.mergable_with(generator2)

    def test_merge(self):
        generator1 = BurnerGenerator("burner-generator")
        generator2 = BurnerGenerator("burner-generator", tags={"some": "stuff"})

        generator1.merge(generator2)
        del generator2

        assert generator1.tags == {"some": "stuff"}

    def test_eq(self):
        generator1 = BurnerGenerator("burner-generator")
        generator2 = BurnerGenerator("burner-generator")

        assert generator1 == generator2

        generator1.tags = {"some": "stuff"}

        assert generator1 != generator2

        container = Container()

        assert generator1 != container
        assert generator2 != container

        # hashable
        assert isinstance(generator1, Hashable)
