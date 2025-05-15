# test_boiler.py

from draftsman.constants import Inventory
from draftsman.entity import Boiler, boilers, Container
from draftsman.error import InvalidEntityError
from draftsman.warning import UnknownEntityWarning, UnknownKeywordWarning

from collections.abc import Hashable
import pytest


@pytest.fixture
def valid_boiler():
    if len(boilers) == 0:
        return None
    return Boiler(
        "boiler",
        id="test",
        quality="uncommon",
        tile_position=(1, 1),
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


class TestBoiler:
    def test_constructor_init(self):
        boiler = Boiler("boiler")

        # Warnings
        with pytest.warns(UnknownEntityWarning):
            Boiler("not a boiler").validate().reissue_all()

        # Errors

    def test_json_schema(self):
        assert Boiler.json_schema(version=(1, 0)) == {
            "$id": "urn:factorio:entity:boiler",
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
        assert Boiler.json_schema(version=(2, 0)) == {
            "$id": "urn:factorio:entity:boiler",
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
                "tags": {"type": "object"},
            },
            "required": ["entity_number", "name", "position"],
        }

    def test_mergable_with(self):
        boiler1 = Boiler("boiler")
        boiler2 = Boiler("boiler", tags={"some": "stuff"})

        assert boiler1.mergable_with(boiler2)
        assert boiler2.mergable_with(boiler1)

        boiler2.tile_position = [-10, -10]
        assert not boiler1.mergable_with(boiler2)

    def test_merge(self):
        boiler1 = Boiler("boiler")
        boiler2 = Boiler("boiler", tags={"some": "stuff"})

        boiler1.merge(boiler2)
        del boiler2

        assert boiler1.tags == {"some": "stuff"}

    def test_eq(self):
        boiler1 = Boiler("boiler")
        boiler2 = Boiler("boiler")

        assert boiler1 == boiler2

        boiler1.set_item_request("coal", 10)

        assert boiler1 != boiler2

        container = Container()

        assert boiler1 != container
        assert boiler2 != container

        # hashable
        assert isinstance(boiler1, Hashable)
