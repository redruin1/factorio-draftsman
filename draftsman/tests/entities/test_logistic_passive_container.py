# test_logistic_passive_container.py
# -*- encoding: utf-8 -*-

from __future__ import unicode_literals

from draftsman.entity import LogisticPassiveContainer, logistic_passive_containers
from draftsman.error import InvalidEntityError, DataFormatError
from draftsman.warning import DraftsmanWarning

from schema import SchemaError

import sys

if sys.version_info >= (3, 3):  # pragma: no coverage
    from unittest import TestCase
else:  # pragma: no coverage
    from unittest2 import TestCase


class LogisticPassiveContainerTesting(TestCase):
    def test_constructor_init(self):
        passive_chest = LogisticPassiveContainer(
            "logistic-chest-passive-provider",
            tile_position=[15, 3],
            bar=5,
            connections={
                "1": {
                    "red": [
                        {"entity_id": "another_entity"},
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
                            {"entity_id": "another_entity"},
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
