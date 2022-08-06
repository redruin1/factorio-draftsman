# test_logistic_active_container.py
# -*- encoding: utf-8 -*-

from __future__ import unicode_literals

from draftsman.entity import LogisticActiveContainer, logistic_active_containers
from draftsman.error import InvalidEntityError, DataFormatError
from draftsman.warning import DraftsmanWarning

import sys

if sys.version_info >= (3, 3):  # pragma: no coverage
    import unittest
else:  # pragma: no coverage
    import unittest2 as unittest


class ContainerTesting(unittest.TestCase):
    def test_constructor_init(self):
        active_chest = LogisticActiveContainer(
            "logistic-chest-active-provider",
            tile_position={"x": 15, "y": 3},
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
            active_chest.to_dict(),
            {
                "name": "logistic-chest-active-provider",
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
        active_chest = LogisticActiveContainer(
            "logistic-chest-active-provider",
            position={"x": 15.5, "y": 1.5},
            bar=5,
            tags={"A": "B"},
        )
        self.assertEqual(
            active_chest.to_dict(),
            {
                "name": "logistic-chest-active-provider",
                "position": {"x": 15.5, "y": 1.5},
                "bar": 5,
                "tags": {"A": "B"},
            },
        )
        # Warnings
        with self.assertWarns(DraftsmanWarning):
            LogisticActiveContainer(
                "logistic-chest-active-provider", position=[0, 0], invalid_keyword="100"
            )
        # Errors
        # Raises InvalidEntityID when not in containers
        with self.assertRaises(InvalidEntityError):
            LogisticActiveContainer("this is not an active provider chest")

        # Raises schema errors when any of the associated data is incorrect
        with self.assertRaises(TypeError):
            LogisticActiveContainer("logistic-chest-active-provider", id=25)

        with self.assertRaises(TypeError):
            LogisticActiveContainer(
                "logistic-chest-active-provider", position=TypeError
            )

        with self.assertRaises(TypeError):
            LogisticActiveContainer(
                "logistic-chest-active-provider", bar="not even trying"
            )

        with self.assertRaises(DataFormatError):
            LogisticActiveContainer(
                "logistic-chest-active-provider",
                connections={"this is": ["very", "wrong"]},
            )

    def test_power_and_circuit_flags(self):
        for container_name in logistic_active_containers:
            container = LogisticActiveContainer(container_name)
            self.assertEqual(container.power_connectable, False)
            self.assertEqual(container.dual_power_connectable, False)
            self.assertEqual(container.circuit_connectable, True)
            self.assertEqual(container.dual_circuit_connectable, False)

    def test_mergable_with(self):
        container1 = LogisticActiveContainer("logistic-chest-active-provider")
        container2 = LogisticActiveContainer(
            "logistic-chest-active-provider", bar=10, tags={"some": "stuff"}
        )

        self.assertTrue(container1.mergable_with(container1))

        self.assertTrue(container1.mergable_with(container2))
        self.assertTrue(container2.mergable_with(container1))

        container2.tile_position = (1, 1)
        self.assertFalse(container1.mergable_with(container2))

    def test_merge(self):
        container1 = LogisticActiveContainer("logistic-chest-active-provider")
        container2 = LogisticActiveContainer(
            "logistic-chest-active-provider", bar=10, tags={"some": "stuff"}
        )

        container1.merge(container2)
        del container2

        self.assertEqual(container1.bar, 10)
        self.assertEqual(container1.tags, {"some": "stuff"})
