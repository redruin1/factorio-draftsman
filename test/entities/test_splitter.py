# test_splitter.py
# -*- encoding: utf-8 -*-

from __future__ import unicode_literals

from draftsman.constants import Direction
from draftsman.entity import Splitter, splitters
from draftsman.error import InvalidEntityError, InvalidSideError, InvalidItemError
from draftsman.warning import DraftsmanWarning

from schema import SchemaError

import sys

if sys.version_info >= (3, 3):  # pragma: no coverage
    from unittest import TestCase
else:  # pragma: no coverage
    from unittest2 import TestCase


class SplitterTesting(TestCase):
    def test_constructor_init(self):
        # Valid
        splitter = Splitter(
            "splitter",
            direction=Direction.EAST,
            tile_position=[1, 1],
            input_priority="left",
            output_priority="right",
            filter="small-lamp",
        )
        self.assertEqual(
            splitter.to_dict(),
            {
                "name": "splitter",
                "position": {"x": 1.5, "y": 2.0},
                "direction": 2,
                "input_priority": "left",
                "output_priority": "right",
                "filter": "small-lamp",
            },
        )

        # Warnings
        with self.assertWarns(DraftsmanWarning):
            Splitter(position=[0, 0], direction=Direction.WEST, invalid_keyword=5)

        # Errors
        # Raises InvalidEntityID when not in containers
        with self.assertRaises(InvalidEntityError):
            Splitter("this is not a splitter")

        # Raises errors when any of the associated data is incorrect
        with self.assertRaises(TypeError):
            Splitter("splitter", id=25)

        with self.assertRaises(TypeError):
            Splitter("splitter", position=TypeError)

        with self.assertRaises(ValueError):
            Splitter("splitter", direction="incorrect")

        with self.assertRaises(TypeError):
            Splitter("splitter", input_priority=TypeError)

        with self.assertRaises(InvalidSideError):
            Splitter("splitter", input_priority="wrong")

        with self.assertRaises(TypeError):
            Splitter("splitter", output_priority=TypeError)

        with self.assertRaises(InvalidSideError):
            Splitter("splitter", output_priority="wrong")

        with self.assertRaises(TypeError):
            Splitter("splitter", filter=TypeError)

        with self.assertRaises(InvalidItemError):
            Splitter("splitter", filter="wrong")

    def test_power_and_circuit_flags(self):
        for name in splitters:
            splitter = Splitter(name)
            self.assertEqual(splitter.power_connectable, False)
            self.assertEqual(splitter.dual_power_connectable, False)
            self.assertEqual(splitter.circuit_connectable, False)
            self.assertEqual(splitter.dual_circuit_connectable, False)
