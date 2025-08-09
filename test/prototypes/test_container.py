# test_container.py

from draftsman import DEFAULT_FACTORIO_VERSION
from draftsman.constants import InventoryType, ValidationMode
from draftsman.data import mods
from draftsman.entity import Container, containers, Accumulator
from draftsman.error import (
    DataFormatError,
)
from draftsman.signatures import (
    BlueprintInsertPlan,
    ItemID,
    ItemInventoryPositions,
    InventoryPosition,
)
import draftsman.validators
from draftsman.warning import (
    BarWarning,
    ItemCapacityWarning,
    UnknownEntityWarning,
    UnknownItemWarning,
    UnknownKeywordWarning,
)

from collections.abc import Hashable
import pytest


@pytest.fixture
def valid_container():
    return Container(
        "wooden-chest",
        id="test",
        quality="uncommon",
        tile_position=(1, 1),
        item_requests=[
            BlueprintInsertPlan(
                id="iron-ore",
                items=ItemInventoryPositions(
                    in_inventory=[
                        InventoryPosition(
                            inventory=InventoryType.CHEST, stack=0, count=50
                        )
                    ]
                ),
            )
        ],
        tags={"blah": "blah"},
    )


class TestContainer:
    def test_constructor_init(self):
        wooden_chest = Container(
            "wooden-chest",
            tile_position=[15, 3],
            bar=5,
        )
        assert wooden_chest.to_dict() == {
            "name": "wooden-chest",
            "position": {"x": 15.5, "y": 3.5},
            "bar": 5,
        }
        wooden_chest = Container(
            "wooden-chest", position={"x": 15.5, "y": 1.5}, bar=5, tags={"A": "B"}
        )
        assert wooden_chest.to_dict() == {
            "name": "wooden-chest",
            "position": {"x": 15.5, "y": 1.5},
            "bar": 5,
            "tags": {"A": "B"},
        }

        # Warnings
        with pytest.warns(UnknownEntityWarning):
            Container("this is not a container").validate().reissue_all()

        # Errors
        # Raises schema errors when any of the associated data is incorrect
        with pytest.raises(TypeError):
            Container("wooden-chest", id=25).validate().reissue_all()
        with pytest.raises(DataFormatError):
            Container("wooden-chest", position=TypeError).validate().reissue_all()
        with pytest.raises(DataFormatError):
            Container("wooden-chest", bar="not even trying").validate().reissue_all()

    def test_power_and_circuit_flags(self):
        for container_name in containers:
            container = Container(container_name)
            assert container.power_connectable == False
            assert container.dual_power_connectable == False
            assert container.circuit_connectable == True
            assert container.dual_circuit_connectable == False

    def test_bar(self):
        container = Container("wooden-chest")

        # Normal operation
        container.bar = 10
        assert container.bar == 10

        # No warning, because it's pedantic level
        container.bar = 100
        assert container.bar == 100

        with draftsman.validators.set_mode(ValidationMode.PEDANTIC):
            # Normal operation
            container.bar = 10
            assert container.bar == 10

            # Pedantic warning
            with pytest.warns(BarWarning):
                container.bar = 100
            assert container.bar == 100

        # Disabled bar
        if mods.versions.get("base", DEFAULT_FACTORIO_VERSION) < (2, 0):
            container = Container("big-ship-wreck-1")
        else:
            # Since no chest with disabled bar on 2.0 exists, we coerce the data
            # to fit
            container = Container("crash-site-chest-1")
            container.prototype["inventory_type"] = "normal"
        with pytest.warns(BarWarning):
            container.bar = 2

        with draftsman.validators.set_mode(ValidationMode.MINIMUM):
            container.bar = 2
            assert container.bar == 2

        # Make sure an unknown entity issues error if out of range...
        with pytest.warns(UnknownEntityWarning):
            container = Container("unknown-container")
        with pytest.raises(DataFormatError):
            container.bar = -1

        # But no warning since inventory size is unknown
        assert container.size is None
        container.bar = 100  # Nothing

    def test_set_item_request(self):
        container = Container("wooden-chest")

        container.set_item_request(
            "iron-plate", 50, inventory=InventoryType.CHEST, slot=0
        )
        container.set_item_request(
            "iron-plate", 50, inventory=InventoryType.CHEST, slot=3
        )
        assert container.item_requests == [
            BlueprintInsertPlan(
                id=ItemID(name="iron-plate"),
                items=ItemInventoryPositions(
                    in_inventory=[
                        InventoryPosition(
                            inventory=InventoryType.CHEST, stack=0, count=50
                        ),
                        InventoryPosition(
                            inventory=InventoryType.CHEST, stack=3, count=50
                        ),
                    ]
                ),
            )
        ]
        assert container.slots_occupied == 2

        # TODO: emit warning that two different items occupy the same slot
        container.set_item_request(
            "iron-ore", 50, inventory=InventoryType.CHEST, slot=0
        )
        assert container.item_requests == [
            BlueprintInsertPlan(
                id=ItemID(name="iron-plate"),
                items=ItemInventoryPositions(
                    in_inventory=[
                        InventoryPosition(
                            inventory=InventoryType.CHEST, stack=0, count=50
                        ),
                        InventoryPosition(
                            inventory=InventoryType.CHEST, stack=3, count=50
                        ),
                    ]
                ),
            ),
            BlueprintInsertPlan(
                id=ItemID(name="iron-ore"),
                items=ItemInventoryPositions(
                    in_inventory=[
                        InventoryPosition(
                            inventory=InventoryType.CHEST, stack=0, count=50
                        )
                    ]
                ),
            ),
        ]
        assert container.slots_occupied == 2

        # TODO: reimplement
        # with pytest.warns(ItemCapacityWarning):
        #     container.set_item_request("copper-plate", 50, slot=100)

        # assert container.items == {"iron-plate": 100, "copper-plate": 10000}
        # assert container.inventory_slots_occupied == 101

        # # container.set_item_requests(None)
        # container.items = {}
        # assert container.items == {}
        # assert container.inventory_slots_occupied == 0

        # with pytest.raises(DataFormatError):
        #     container.set_item_request(TypeError, 100)
        # with pytest.warns(UnknownItemWarning):
        #     container.set_item_request("unknown", 100)
        # with pytest.raises(DataFormatError):
        #     container.set_item_request("iron-plate", TypeError)
        # with pytest.raises(DataFormatError):
        #     container.set_item_request("iron-plate", -1)

        # assert container.items == {"unknown": 100}
        # assert container.inventory_slots_occupied == 0

        # with pytest.raises(DataFormatError):
        #     container.items = {"incorrect", "format"}
        # assert container.items == {"unknown": 100}

        with pytest.raises(DataFormatError):
            ItemInventoryPositions(in_inventory="incorrect")

    def test_mergable_with(self):
        container1 = Container("wooden-chest")
        container2 = Container("wooden-chest", bar=10)

        assert container1.mergable_with(container2)
        assert container2.mergable_with(container1)

        container2.tile_position = (1, 1)
        assert not container1.mergable_with(container2)

    def test_merge(self):
        container1 = Container("wooden-chest")
        container2 = Container("wooden-chest", bar=10)

        container1.merge(container2)
        del container2

        assert container1.bar == 10

    def test_eq(self):
        container1 = Container("wooden-chest")
        container2 = Container("wooden-chest")

        assert container1 == container2

        container1.bar = 4

        assert container1 != container2

        container = Accumulator()

        assert container1 != container
        assert container2 != container

        # hashable
        assert isinstance(container1, Hashable)
