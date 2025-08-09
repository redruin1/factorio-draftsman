# test_beacon.py

from draftsman.constants import InventoryType
from draftsman.entity import Beacon, beacons, Container
from draftsman.error import DataFormatError
from draftsman.signatures import (
    BlueprintInsertPlan,
    ItemID,
    ItemInventoryPositions,
    InventoryPosition,
)
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


@pytest.fixture
def valid_beacon():
    return Beacon(
        "beacon",
        id="test",
        quality="uncommon",
        tile_position=(1, 1),
        item_requests=[
            {
                "id": {"name": "speed-module"},
                "items": {"in_inventory": [{"inventory": 1, "stack": 0}]},
            }
        ],
        tags={"blah": "blah"},
    )


class TestBeacon:
    def test_contstructor_init(self):
        beacon = Beacon()

        with pytest.warns(UnknownEntityWarning):
            Beacon("this is not a beacon").validate().reissue_all()

    def test_request_modules(self):
        beacon = Beacon("beacon")
        assert beacon.module_slots_occupied == 0

        beacon.request_modules("speed-module-3", 0, "legendary")
        assert beacon.item_requests == [
            BlueprintInsertPlan(
                id=ItemID(name="speed-module-3", quality="legendary"),
                items=ItemInventoryPositions(
                    in_inventory=[
                        InventoryPosition(
                            inventory=InventoryType.BEACON_MODULES,
                            stack=0,
                        ),
                    ]
                ),
            )
        ]
        assert beacon.module_slots_occupied == 1

        # Cannot put prod modules in a (vanilla) beacon
        # with pytest.warns(ModuleNotAllowedWarning): # TODO
        beacon.request_modules("productivity-module-3", 1, "legendary")
        assert beacon.item_requests == [
            BlueprintInsertPlan(
                id=ItemID(name="speed-module-3", quality="legendary"),
                items=ItemInventoryPositions(
                    in_inventory=[
                        InventoryPosition(
                            inventory=InventoryType.BEACON_MODULES,
                            stack=0,
                        ),
                    ]
                ),
            ),
            BlueprintInsertPlan(
                id=ItemID(name="productivity-module-3", quality="legendary"),
                items=ItemInventoryPositions(
                    in_inventory=[
                        InventoryPosition(
                            inventory=InventoryType.BEACON_MODULES,
                            stack=1,
                        ),
                    ]
                ),
            ),
        ]
        assert beacon.module_slots_occupied == 2

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
