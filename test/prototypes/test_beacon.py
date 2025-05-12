# test_beacon.py

from draftsman.entity import Beacon, beacons, Container
from draftsman.error import DataFormatError
from draftsman.warning import (
    ModuleCapacityWarning,
    ModuleNotAllowedWarning,
    ItemLimitationWarning,
    UnknownEntityWarning,
    UnknownItemWarning,
    UnknownKeywordWarning,
)

from collections.abc import Hashable
import pytest


valid_beacon = Beacon(
    "beacon",
    id="test",
    quality="uncommon",
    tile_position=(1, 1),
    item_requests=[
        {
            "id": {
                "name": "speed-module"
            },
            "items": {
                "in_inventory": [
                    {
                        "inventory": 1,
                        "stack": 0
                    }
                ]
            }
        }
    ],
    tags={"blah": "blah"},
)


class TestBeacon:
    def test_contstructor_init(self):
        beacon = Beacon()

        with pytest.warns(UnknownEntityWarning):
            Beacon("this is not a beacon").validate().reissue_all()

    def test_json_schema(self):
        assert Beacon.json_schema(version=(1, 0)) == {
            "$id": "urn:factorio:entity:beacon",
            "$schema": "https://json-schema.org/draft/2020-12/schema",
            "type": "object",
            "properties": {
                "entity_number": {"$ref": "urn:uint64"},
                "name": {"type": "string"},
                "position": {"$ref": "urn:factorio:position"},
                "items": {
                    "type": "array",
                    "items": {"$ref": "urn:factorio:item-request"}
                },
                "tags": {"type": "object"}
            },
            "required": ["entity_number", "name", "position"]
        }
        assert Beacon.json_schema(version=(2, 0)) == {
            "$id": "urn:factorio:entity:beacon",
            "$schema": "https://json-schema.org/draft/2020-12/schema",
            "type": "object",
            "properties": {
                "entity_number": {"$ref": "urn:uint64"},
                "name": {"type": "string"},
                "position": {"$ref": "urn:factorio:position"},
                "quality": {"$ref": "urn:factorio:quality-name"},
                "items": {
                    "type": "array",
                    "items": {"$ref": "urn:factorio:item-request"}
                },
                "tags": {"type": "object"}
            },
            "required": ["entity_number", "name", "position"]
        }

    # def test_set_item_request(self):
    #     beacon = Beacon()
    #     beacon.set_item_request("speed-module-3", 1)
    #     assert beacon.items == {"speed-module-3": 1}

    #     assert beacon.total_module_slots == 2
    #     with pytest.warns(ModuleCapacityWarning):
    #         beacon.set_item_request("effectivity-module-3", 3)

    #     beacon.items = None
    #     assert beacon.allowed_modules == {
    #         "speed-module",
    #         "speed-module-2",
    #         "speed-module-3",
    #         "effectivity-module",
    #         "effectivity-module-2",
    #         "effectivity-module-3",
    #     }
    #     with pytest.warns(ModuleNotAllowedWarning):
    #         beacon.set_item_request("productivity-module-3", 1)

    #     beacon.items = None
    #     with pytest.warns(ItemLimitationWarning):
    #         beacon.set_item_request("steel-plate", 2)

    #     # Errors
    #     beacon.items = None
    #     with pytest.raises(DataFormatError):
    #         beacon.set_item_request("incorrect", "nonsense")
    #     with pytest.warns(UnknownItemWarning):
    #         beacon.set_item_request("unknown", 100)
    #     with pytest.raises(DataFormatError):
    #         beacon.set_item_request("speed-module-2", "nonsense")
    #     with pytest.raises(DataFormatError):
    #         beacon.set_item_request("speed-module-2", -1)

    #     assert beacon.items == {"unknown": 100}
    #     assert beacon.module_slots_occupied == 0

    def test_mergable_with(self):
        beacon1 = Beacon("beacon")
        beacon2 = Beacon("beacon", tags={"some": "stuff"})

        assert beacon1.mergable_with(beacon2)
        assert beacon2.mergable_with(beacon1)

        beacon2.tile_position = (1, 1)
        assert not beacon1.mergable_with(beacon2)

    def test_merge(self):
        beacon1 = Beacon("beacon")
        beacon2 = Beacon("beacon")

        beacon1.merge(beacon2)
        del beacon2

    def test_eq(self):
        beacon1 = Beacon("beacon")
        beacon2 = Beacon("beacon")

        assert beacon1 == beacon2

        # beacon1.set_item_request("speed-module-3", 2)
        beacon1.tags = {"something": "else"}

        assert beacon1 != beacon2

        container = Container()

        assert beacon1 != container
        assert beacon2 != container

        # hashable
        assert isinstance(beacon1, Hashable)
