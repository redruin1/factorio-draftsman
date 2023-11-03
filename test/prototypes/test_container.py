# test_container.py

from draftsman.entity import Container, containers, Accumulator
from draftsman.error import (
    DraftsmanError,
    InvalidEntityError,
    DataFormatError,
    InvalidItemError,
)
from draftsman.warning import BarWarning, ItemCapacityWarning, UnknownEntityWarning, UnknownKeywordWarning

from collections.abc import Hashable
import pytest


class TestContainer:
    def test_constructor_init(self):
        wooden_chest = Container(
            "wooden-chest",
            tile_position=[15, 3],
            bar=5,
            connections={
                "1": {
                    "red": [
                        {"entity_id": 2},
                        {"entity_id": 2, "circuit_id": 1},
                    ]
                }
            },
        )
        assert wooden_chest.to_dict() == {
            "name": "wooden-chest",
            "position": {"x": 15.5, "y": 3.5},
            "bar": 5,
            "connections": {
                "1": {
                    "red": [
                        {"entity_id": 2},
                        {"entity_id": 2, "circuit_id": 1},
                    ]
                }
            },
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
        with pytest.warns(UnknownKeywordWarning):
            Container("wooden-chest", position=[0, 0], invalid_keyword="100")
        with pytest.warns(UnknownKeywordWarning):
            Container("wooden-chest", connections={"this is": ["very", "wrong"]})
        with pytest.warns(UnknownEntityWarning):
            Container("this is not a container")

        # Errors
        # Raises schema errors when any of the associated data is incorrect
        with pytest.raises(TypeError):
            Container("wooden-chest", id=25)
        with pytest.raises(TypeError):
            Container("wooden-chest", position=TypeError)
        with pytest.raises(DataFormatError):
            Container("wooden-chest", bar="not even trying")
        with pytest.raises(DataFormatError):
            Container("wooden-chest", connections="incorrect")

    def test_power_and_circuit_flags(self):
        for container_name in containers:
            container = Container(container_name)
            assert container.power_connectable == False
            assert container.dual_power_connectable == False
            assert container.circuit_connectable == True
            assert container.dual_circuit_connectable == False

    def test_bar_with_disabled_containers(self):
        container = Container("big-ship-wreck-1")
        with pytest.warns(BarWarning):
            container.bar = 2

    def test_set_item_request(self):
        container = Container("wooden-chest")

        container.set_item_request("iron-plate", 50)
        assert container.items == {"iron-plate": 50}
        assert container.inventory_slots_occupied == 1

        container.set_item_request("iron-plate", 100)
        assert container.items == {"iron-plate": 100}
        assert container.inventory_slots_occupied == 1

        with pytest.warns(ItemCapacityWarning):
            container.set_item_request("copper-plate", 10000)

        assert container.items == {"iron-plate": 100, "copper-plate": 10000}
        assert container.inventory_slots_occupied == 101

        # container.set_item_requests(None)
        container.items = {}
        assert container.items == {}
        assert container.inventory_slots_occupied == 0

        with pytest.raises(TypeError):
            container.set_item_request(TypeError, 100)
        # with pytest.raises(InvalidItemError): # TODO
        #     container.set_item_request("incorrect", 100)
        with pytest.raises(TypeError):
            container.set_item_request("iron-plate", TypeError)
        # with pytest.raises(ValueError): # TODO
        #     container.set_item_request("iron-plate", -1)

        assert container.items == {}
        assert container.inventory_slots_occupied == 0

    def test_mergable_with(self):
        container1 = Container("wooden-chest")
        container2 = Container("wooden-chest", bar=10, items={"copper-plate": 100})

        assert container1.mergable_with(container2)
        assert container2.mergable_with(container1)

        container2.tile_position = (1, 1)
        assert not container1.mergable_with(container2)

    def test_merge(self):
        container1 = Container("wooden-chest")
        container2 = Container("wooden-chest", bar=10, items={"copper-plate": 100})

        container1.merge(container2)
        del container2

        assert container1.bar == 10
        assert container1.items == {"copper-plate": 100}

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
