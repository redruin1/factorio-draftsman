# test_logistic_storage_container.py
# -*- encoding: utf-8 -*-

from __future__ import unicode_literals

from draftsman.entity import LogisticStorageContainer, logistic_storage_containers
from draftsman.error import InvalidEntityError, DataFormatError
from draftsman.warning import DraftsmanWarning

import sys

if sys.version_info >= (3, 3):  # pragma: no coverage
    import unittest
else:  # pragma: no coverage
    import unittest2 as unittest


class LogisticStorageContainerTesting(unittest.TestCase):
    def test_constructor_init(self):
        storage_chest = LogisticStorageContainer(
            "logistic-chest-storage",
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
            storage_chest.to_dict(),
            {
                "name": "logistic-chest-storage",
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

        storage_chest = LogisticStorageContainer(
            request_filters=[{"index": 1, "name": "iron-ore", "count": 100}]
        )
        self.assertEqual(
            storage_chest.to_dict(),
            {
                "name": "logistic-chest-storage",
                "position": {"x": 0.5, "y": 0.5},
                "request_filters": [{"index": 1, "name": "iron-ore", "count": 100}],
            },
        )

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

    def test_mergable_with(self):
        container1 = LogisticStorageContainer("logistic-chest-storage")
        container2 = LogisticStorageContainer(
            "logistic-chest-storage",
            bar=10,
            request_filters=[{"name": "utility-science-pack", "index": 1, "count": 0}],
            tags={"some": "stuff"},
        )

        self.assertTrue(container1.mergable_with(container1))

        self.assertTrue(container1.mergable_with(container2))
        self.assertTrue(container2.mergable_with(container1))

        container2.tile_position = (1, 1)
        self.assertFalse(container1.mergable_with(container2))

    def test_merge(self):
        container1 = LogisticStorageContainer("logistic-chest-storage")
        container2 = LogisticStorageContainer(
            "logistic-chest-storage",
            bar=10,
            request_filters=[{"name": "utility-science-pack", "index": 1, "count": 0}],
            tags={"some": "stuff"},
        )

        container1.merge(container2)
        del container2

        self.assertEqual(container1.bar, 10)
        self.assertEqual(
            container1.request_filters,
            [{"name": "utility-science-pack", "index": 1, "count": 0}],
        )
        self.assertEqual(container1.tags, {"some": "stuff"})
