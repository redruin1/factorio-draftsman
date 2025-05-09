# test_container.py

from draftsman.constants import Inventory, ValidationMode
from draftsman.entity import Container, containers, Accumulator
from draftsman.error import (
    DataFormatError,
)
from draftsman.signatures import (
    AttrsItemRequest,
    AttrsItemID,
    AttrsItemSpecification,
    AttrsInventoryLocation,
)
from draftsman.warning import (
    BarWarning,
    ItemCapacityWarning,
    UnknownEntityWarning,
    UnknownItemWarning,
    UnknownKeywordWarning,
)

from collections.abc import Hashable
import pytest


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

        # No warning, because it's pedantic level
        container.bar = 100
        assert container.bar == 100

        container.validate_assignment = "pedantic"
        assert container.validate_assignment == ValidationMode.PEDANTIC

        container.bar = 10
        assert container.bar == 10

        with pytest.warns(BarWarning):
            container.bar = 100
        assert container.bar == 100

        # Disabled bar
        # Since no chest with disabled bar exists, we coerce the data to fit
        container = Container("crash-site-chest-1")
        container.prototype["inventory_type"] = "normal"
        with pytest.warns(BarWarning):
            container.bar = 2

        container.validate_assignment = "minimum"
        assert container.validate_assignment == ValidationMode.MINIMUM

        container.bar = 2
        assert container.bar == 2

    def test_set_item_request(self):  # TODO: reimplement
        container = Container("wooden-chest")

        container.set_item_request("iron-plate", 50, inventory=Inventory.chest, slot=0)
        container.set_item_request("iron-plate", 50, inventory=Inventory.chest, slot=3)
        assert container.item_requests == [
            AttrsItemRequest(
                id=AttrsItemID(name="iron-plate"),
                items=AttrsItemSpecification(
                    in_inventory=[
                        AttrsInventoryLocation(
                            inventory=Inventory.chest, stack=0, count=50
                        ),
                        AttrsInventoryLocation(
                            inventory=Inventory.chest, stack=3, count=50
                        ),
                    ]
                ),
            )
        ]
        assert container.inventory_slots_occupied == 2

        container.set_item_request("iron-ore", 50, inventory=Inventory.chest, slot=0)
        assert container.item_requests == [
            AttrsItemRequest(
                id=AttrsItemID(name="iron-plate"),
                items=AttrsItemSpecification(
                    in_inventory=[
                        AttrsInventoryLocation(
                            inventory=Inventory.chest, stack=0, count=50
                        ),
                        AttrsInventoryLocation(
                            inventory=Inventory.chest, stack=3, count=50
                        ),
                    ]
                ),
            ),
            AttrsItemRequest(
                id=AttrsItemID(name="iron-ore"),
                items=AttrsItemSpecification(
                    in_inventory=[
                        AttrsInventoryLocation(
                            inventory=Inventory.chest, stack=0, count=50
                        )
                    ]
                ),
            ),
        ]
        assert container.inventory_slots_occupied == 2

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
            AttrsItemSpecification(in_inventory="incorrect")

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
