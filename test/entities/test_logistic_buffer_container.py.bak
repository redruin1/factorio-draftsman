# test_logistic_buffer_container.py
# -*- encoding: utf-8 -*-

from __future__ import unicode_literals

from draftsman.entity import LogisticBufferContainer, logistic_buffer_containers
from draftsman.error import InvalidEntityError, DataFormatError
from draftsman.warning import DraftsmanWarning

import sys

if sys.version_info >= (3, 3):  # pragma: no coverage
    import unittest
else:  # pragma: no coverage
    import unittest2 as unittest


class LogisticBufferContainerTesting(unittest.TestCase):
    def test_constructor_init(self):
        buffer_chest = LogisticBufferContainer(
            "logistic-chest-buffer",
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
            buffer_chest.to_dict(),
            {
                "name": "logistic-chest-buffer",
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
        buffer_chest = LogisticBufferContainer(
            "logistic-chest-buffer",
            position={"x": 15.5, "y": 1.5},
            bar=5,
            tags={"A": "B"},
        )
        self.assertEqual(
            buffer_chest.to_dict(),
            {
                "name": "logistic-chest-buffer",
                "position": {"x": 15.5, "y": 1.5},
                "bar": 5,
                "tags": {"A": "B"},
            },
        )

        buffer_chest = LogisticBufferContainer(request_filters=[("iron-ore", 100)])
        self.assertEqual(
            buffer_chest.to_dict(),
            {
                "name": "logistic-chest-buffer",
                "position": {"x": 0.5, "y": 0.5},
                "request_filters": [{"index": 1, "name": "iron-ore", "count": 100}],
            },
        )

        buffer_chest = LogisticBufferContainer(
            request_filters=[{"index": 1, "name": "iron-ore", "count": 100}]
        )
        self.assertEqual(
            buffer_chest.to_dict(),
            {
                "name": "logistic-chest-buffer",
                "position": {"x": 0.5, "y": 0.5},
                "request_filters": [{"index": 1, "name": "iron-ore", "count": 100}],
            },
        )

        # Warnings
        with self.assertWarns(DraftsmanWarning):
            LogisticBufferContainer(
                "logistic-chest-buffer", position=[0, 0], invalid_keyword="100"
            )

        # Errors
        # Raises InvalidEntityID when not in containers
        with self.assertRaises(InvalidEntityError):
            LogisticBufferContainer("this is not a logistics storage chest")

        # Raises schema errors when any of the associated data is incorrect
        with self.assertRaises(TypeError):
            LogisticBufferContainer("logistic-chest-buffer", id=25)

        with self.assertRaises(TypeError):
            LogisticBufferContainer("logistic-chest-buffer", position=TypeError)

        with self.assertRaises(TypeError):
            LogisticBufferContainer("logistic-chest-buffer", bar="not even trying")

        with self.assertRaises(DataFormatError):
            LogisticBufferContainer(
                "logistic-chest-buffer", connections={"this is": ["very", "wrong"]}
            )

        with self.assertRaises(DataFormatError):
            LogisticBufferContainer(
                "logistic-chest-buffer", request_filters={"this is": ["very", "wrong"]}
            )

        with self.assertRaises(DataFormatError):
            LogisticBufferContainer(control_behavior={"unused_key": "something"})

    def test_power_and_circuit_flags(self):
        for name in logistic_buffer_containers:
            container = LogisticBufferContainer(name)
            self.assertEqual(container.power_connectable, False)
            self.assertEqual(container.dual_power_connectable, False)
            self.assertEqual(container.circuit_connectable, True)
            self.assertEqual(container.dual_circuit_connectable, False)

    def test_mergable_with(self):
        container1 = LogisticBufferContainer("logistic-chest-buffer")
        container2 = LogisticBufferContainer(
            "logistic-chest-buffer",
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
        container1 = LogisticBufferContainer("logistic-chest-buffer")
        container2 = LogisticBufferContainer(
            "logistic-chest-buffer",
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
