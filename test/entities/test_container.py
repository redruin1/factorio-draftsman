# test_container.py
# -*- encoding: utf-8 -*-

from __future__ import unicode_literals

from draftsman.entity import Container, containers
from draftsman.error import (
    DraftsmanError,
    InvalidEntityError,
    DataFormatError,
    InvalidItemError,
)
from draftsman.warning import DraftsmanWarning, ItemCapacityWarning

import sys

if sys.version_info >= (3, 3):  # pragma: no coverage
    import unittest
else:  # pragma: no coverage
    import unittest2 as unittest


class ContainerTesting(unittest.TestCase):
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
        self.assertEqual(
            wooden_chest.to_dict(),
            {
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
            },
        )
        wooden_chest = Container(
            "wooden-chest", position={"x": 15.5, "y": 1.5}, bar=5, tags={"A": "B"}
        )
        self.assertEqual(
            wooden_chest.to_dict(),
            {
                "name": "wooden-chest",
                "position": {"x": 15.5, "y": 1.5},
                "bar": 5,
                "tags": {"A": "B"},
            },
        )
        # Warnings
        with self.assertWarns(DraftsmanWarning):
            Container("wooden-chest", position=[0, 0], invalid_keyword="100")
        # Errors
        # Raises InvalidEntityID when not in containers
        with self.assertRaises(InvalidEntityError):
            Container("this is not a container")

        # Raises schema errors when any of the associated data is incorrect
        with self.assertRaises(TypeError):
            Container("wooden-chest", id=25)

        with self.assertRaises(TypeError):
            Container("wooden-chest", position=TypeError)

        with self.assertRaises(TypeError):
            Container("wooden-chest", bar="not even trying")

        with self.assertRaises(DataFormatError):
            Container("wooden-chest", connections={"this is": ["very", "wrong"]})

    def test_power_and_circuit_flags(self):
        for container_name in containers:
            container = Container(container_name)
            self.assertEqual(container.power_connectable, False)
            self.assertEqual(container.dual_power_connectable, False)
            self.assertEqual(container.circuit_connectable, True)
            self.assertEqual(container.dual_circuit_connectable, False)

    def test_bar_with_disabled_containers(self):
        container = Container("big-ship-wreck-1")
        with self.assertRaises(DraftsmanError):
            container.bar = 2

    def test_set_item_request(self):
        container = Container("wooden-chest")

        container.set_item_request("iron-plate", 50)
        self.assertEqual(container.items, {"iron-plate": 50})
        self.assertEqual(container.inventory_slots_occupied, 1)

        container.set_item_request("iron-plate", 100)
        self.assertEqual(container.items, {"iron-plate": 100})
        self.assertEqual(container.inventory_slots_occupied, 1)

        with self.assertWarns(ItemCapacityWarning):
            container.set_item_request("copper-plate", 10000)

        self.assertEqual(container.items, {"iron-plate": 100, "copper-plate": 10000})
        self.assertEqual(container.inventory_slots_occupied, 101)

        container.set_item_requests(None)
        self.assertEqual(container.items, {})
        self.assertEqual(container.inventory_slots_occupied, 0)

        with self.assertRaises(TypeError):
            container.set_item_request(TypeError, 100)
        with self.assertRaises(InvalidItemError):
            container.set_item_request("incorrect", 100)
        with self.assertRaises(TypeError):
            container.set_item_request("iron-plate", TypeError)
        with self.assertRaises(ValueError):
            container.set_item_request("iron-plate", -1)

        self.assertEqual(container.items, {})
        self.assertEqual(container.inventory_slots_occupied, 0)

    def test_mergable_with(self):
        container1 = Container("wooden-chest")
        container2 = Container("wooden-chest", bar=10, items={"copper-plate": 100})

        self.assertTrue(container1.mergable_with(container2))
        self.assertTrue(container2.mergable_with(container1))

        container2.tile_position = (1, 1)
        self.assertFalse(container1.mergable_with(container2))

    def test_merge(self):
        container1 = Container("wooden-chest")
        container2 = Container("wooden-chest", bar=10, items={"copper-plate": 100})

        container1.merge(container2)
        del container2

        self.assertEqual(container1.bar, 10)
        self.assertEqual(container1.items, {"copper-plate": 100})
