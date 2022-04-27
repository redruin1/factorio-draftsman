# test_logistic_storage_container.py
# -*- encoding: utf-8 -*-

from __future__ import unicode_literals

from draftsman.entity import LogisticStorageContainer, logistic_storage_containers
from draftsman.error import InvalidEntityError, DataFormatError
from draftsman.warning import DraftsmanWarning

from schema import SchemaError

import sys

if sys.version_info >= (3, 3):  # pragma: no coverage
    from unittest import TestCase
else:  # pragma: no coverage
    from unittest2 import TestCase


class LogisticStorageContainerTesting(TestCase):
    def test_constructor_init(self):
        storage_chest = LogisticStorageContainer(
            "logistic-chest-storage",
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
            storage_chest.to_dict(),
            {
                "name": "logistic-chest-storage",
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
        storage_chest = LogisticStorageContainer(
            "logistic-chest-storage", position=[15.5, 1.5], bar=5, tags={"A": "B"}
        )
        self.assertEqual(
            storage_chest.to_dict(),
            {
                "name": "logistic-chest-storage",
                "position": {"x": 15.5, "y": 1.5},
                "bar": 5,
                "tags": {"A": "B"},
            },
        )

        storage_chest = LogisticStorageContainer(request_filters=[("iron-ore", 100)])
        self.assertEqual(
            storage_chest.to_dict(),
            {
                "name": "logistic-chest-storage",
                "position": {"x": 0.5, "y": 0.5},
                "request_filters": [{"index": 1, "name": "iron-ore", "count": 100}],
            },
        )
        # TODO
        # storage_chest = LogisticStorageContainer(
        #     request_filters = [
        #         {"index": 1, "name": "iron-ore", "count": 100}
        #     ]
        # )

        # Warnings
        with self.assertWarns(DraftsmanWarning):
            LogisticStorageContainer(
                "logistic-chest-storage", position=[0, 0], invalid_keyword="100"
            )

        # Errors
        # Raises InvalidEntityID when not in containers
        with self.assertRaises(InvalidEntityError):
            LogisticStorageContainer("this is not a logistics storage chest")

        # Raises schema errors when any of the associated data is incorrect
        with self.assertRaises(TypeError):
            LogisticStorageContainer("logistic-chest-storage", id=25)

        with self.assertRaises(TypeError):
            LogisticStorageContainer("logistic-chest-storage", position=TypeError)

        with self.assertRaises(TypeError):
            LogisticStorageContainer("logistic-chest-storage", bar="not even trying")

        with self.assertRaises(DataFormatError):
            LogisticStorageContainer(
                "logistic-chest-storage", connections={"this is": ["very", "wrong"]}
            )

        with self.assertRaises(DataFormatError):
            LogisticStorageContainer(
                "logistic-chest-storage", request_filters={"this is": ["very", "wrong"]}
            )

    def test_power_and_circuit_flags(self):
        for name in logistic_storage_containers:
            container = LogisticStorageContainer(name)
            self.assertEqual(container.power_connectable, False)
            self.assertEqual(container.dual_power_connectable, False)
            self.assertEqual(container.circuit_connectable, True)
            self.assertEqual(container.dual_circuit_connectable, False)
