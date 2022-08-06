# test_logistic_request_container.py
# -*- encoding: utf-8 -*-

from __future__ import unicode_literals

from draftsman.entity import LogisticRequestContainer, logistic_request_containers
from draftsman.error import InvalidEntityError, DataFormatError
from draftsman.warning import DraftsmanWarning

import sys

if sys.version_info >= (3, 3):  # pragma: no coverage
    import unittest
else:  # pragma: no coverage
    import unittest2 as unittest


class LogisticRequestContainerTesting(unittest.TestCase):
    def test_constructor_init(self):
        request_chest = LogisticRequestContainer(
            "logistic-chest-requester",
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
            request_chest.to_dict(),
            {
                "name": "logistic-chest-requester",
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
        request_chest = LogisticRequestContainer(
            "logistic-chest-requester",
            position={"x": 15.5, "y": 1.5},
            bar=5,
            tags={"A": "B"},
        )
        self.assertEqual(
            request_chest.to_dict(),
            {
                "name": "logistic-chest-requester",
                "position": {"x": 15.5, "y": 1.5},
                "bar": 5,
                "tags": {"A": "B"},
            },
        )

        request_chest = LogisticRequestContainer(
            request_from_buffers=True, request_filters=[("iron-ore", 100)]
        )
        self.assertEqual(
            request_chest.to_dict(),
            {
                "name": "logistic-chest-requester",
                "position": {"x": 0.5, "y": 0.5},
                "request_from_buffers": True,
                "request_filters": [{"index": 1, "name": "iron-ore", "count": 100}],
            },
        )

        request_chest = LogisticRequestContainer(
            request_filters=[{"index": 1, "name": "iron-ore", "count": 100}]
        )
        self.assertEqual(
            request_chest.to_dict(),
            {
                "name": "logistic-chest-requester",
                "position": {"x": 0.5, "y": 0.5},
                "request_filters": [{"index": 1, "name": "iron-ore", "count": 100}],
            },
        )

        # Warnings
        with self.assertWarns(DraftsmanWarning):
            LogisticRequestContainer(
                "logistic-chest-requester", position=[0, 0], invalid_keyword="100"
            )

        # Errors
        # Raises InvalidEntityID when not in containers
        with self.assertRaises(InvalidEntityError):
            LogisticRequestContainer("this is not a logistics storage chest")

        # Raises schema errors when any of the associated data is incorrect
        with self.assertRaises(TypeError):
            LogisticRequestContainer("logistic-chest-requester", id=25)

        with self.assertRaises(TypeError):
            LogisticRequestContainer("logistic-chest-requester", position=TypeError)

        with self.assertRaises(TypeError):
            LogisticRequestContainer("logistic-chest-requester", bar="not even trying")

        with self.assertRaises(DataFormatError):
            LogisticRequestContainer(
                "logistic-chest-requester", connections={"this is": ["very", "wrong"]}
            )

        with self.assertRaises(DataFormatError):
            LogisticRequestContainer(
                "logistic-chest-requester",
                request_filters={"this is": ["very", "wrong"]},
            )

        with self.assertRaises(TypeError):
            LogisticRequestContainer(
                "logistic-chest-requester", request_from_buffers="invalid"
            )

        with self.assertRaises(DataFormatError):
            LogisticRequestContainer(control_behavior={"unused_key": "something"})

    def test_power_and_circuit_flags(self):
        for name in logistic_request_containers:
            container = LogisticRequestContainer(name)
            self.assertEqual(container.power_connectable, False)
            self.assertEqual(container.dual_power_connectable, False)
            self.assertEqual(container.circuit_connectable, True)
            self.assertEqual(container.dual_circuit_connectable, False)

    def test_mergable_with(self):
        container1 = LogisticRequestContainer("logistic-chest-requester")
        container2 = LogisticRequestContainer(
            "logistic-chest-requester",
            bar=10,
            request_filters=[{"name": "utility-science-pack", "index": 1, "count": 10}],
            tags={"some": "stuff"},
        )

        self.assertTrue(container1.mergable_with(container1))

        self.assertTrue(container1.mergable_with(container2))
        self.assertTrue(container2.mergable_with(container1))

        container2.tile_position = (1, 1)
        self.assertFalse(container1.mergable_with(container2))

    def test_merge(self):
        container1 = LogisticRequestContainer("logistic-chest-requester")
        container2 = LogisticRequestContainer(
            "logistic-chest-requester",
            bar=10,
            request_filters=[{"name": "utility-science-pack", "index": 1, "count": 10}],
            tags={"some": "stuff"},
        )

        container1.merge(container2)
        del container2

        self.assertEqual(container1.bar, 10)
        self.assertEqual(
            container1.request_filters,
            [{"name": "utility-science-pack", "index": 1, "count": 10}],
        )
        self.assertEqual(container1.tags, {"some": "stuff"})
