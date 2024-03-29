# test_logistic_passive_container.py
# -*- encoding: utf-8 -*-

from __future__ import unicode_literals

from draftsman.entity import LogisticPassiveContainer, logistic_passive_containers
from draftsman.error import InvalidEntityError, DataFormatError
from draftsman.warning import DraftsmanWarning

import sys

if sys.version_info >= (3, 3):  # pragma: no coverage
    import unittest
else:  # pragma: no coverage
    import unittest2 as unittest


class LogisticPassiveContainerTesting(unittest.TestCase):
    def test_constructor_init(self):
        passive_chest = LogisticPassiveContainer(
            "logistic-chest-passive-provider",
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
            passive_chest.to_dict(),
            {
                "name": "logistic-chest-passive-provider",
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
        passive_chest = LogisticPassiveContainer(
            "logistic-chest-passive-provider",
            position={"x": 15.5, "y": 1.5},
            bar=5,
            tags={"A": "B"},
        )
        self.assertEqual(
            passive_chest.to_dict(),
            {
                "name": "logistic-chest-passive-provider",
                "position": {"x": 15.5, "y": 1.5},
                "bar": 5,
                "tags": {"A": "B"},
            },
        )

        # Warnings
        with self.assertWarns(DraftsmanWarning):
            LogisticPassiveContainer(
                "logistic-chest-passive-provider",
                position=[0, 0],
                invalid_keyword="100",
            )

        # Errors
        # Raises InvalidEntityID when not in containers
        with self.assertRaises(InvalidEntityError):
            LogisticPassiveContainer("this is not a logistics passive chest")

        # Raises schema errors when any of the associated data is incorrect
        with self.assertRaises(TypeError):
            LogisticPassiveContainer("logistic-chest-passive-provider", id=25)

        with self.assertRaises(TypeError):
            LogisticPassiveContainer(
                "logistic-chest-passive-provider", position=TypeError
            )

        with self.assertRaises(TypeError):
            LogisticPassiveContainer(
                "logistic-chest-passive-provider", bar="not even trying"
            )

        with self.assertRaises(DataFormatError):
            LogisticPassiveContainer(
                "logistic-chest-passive-provider",
                connections={"this is": ["very", "wrong"]},
            )

    def test_power_and_circuit_flags(self):
        for name in logistic_passive_containers:
            container = LogisticPassiveContainer(name)
            self.assertEqual(container.power_connectable, False)
            self.assertEqual(container.dual_power_connectable, False)
            self.assertEqual(container.circuit_connectable, True)
            self.assertEqual(container.dual_circuit_connectable, False)

    def test_mergable_with(self):
        container1 = LogisticPassiveContainer("logistic-chest-passive-provider")
        container2 = LogisticPassiveContainer(
            "logistic-chest-passive-provider", bar=10, tags={"some": "stuff"}
        )

        self.assertTrue(container1.mergable_with(container1))

        self.assertTrue(container1.mergable_with(container2))
        self.assertTrue(container2.mergable_with(container1))

        container2.tile_position = (1, 1)
        self.assertFalse(container1.mergable_with(container2))

    def test_merge(self):
        container1 = LogisticPassiveContainer("logistic-chest-passive-provider")
        container2 = LogisticPassiveContainer(
            "logistic-chest-passive-provider", bar=10, tags={"some": "stuff"}
        )

        container1.merge(container2)
        del container2

        self.assertEqual(container1.bar, 10)
        self.assertEqual(container1.tags, {"some": "stuff"})
