# test_underground_belt.py
# -*- encoding: utf-8 -*-

from __future__ import unicode_literals

from draftsman.constants import Direction
from draftsman.entity import UndergroundBelt, underground_belts
from draftsman.error import InvalidEntityError, DataFormatError
from draftsman.warning import DraftsmanWarning

from schema import SchemaError

import sys

if sys.version_info >= (3, 3):  # pragma: no coverage
    from unittest import TestCase
else:  # pragma: no coverage
    from unittest2 import TestCase


class UndergroundBeltTesting(TestCase):
    def test_constructor_init(self):
        # Valid
        underground_belt = UndergroundBelt(
            "underground-belt",
            direction=Direction.EAST,
            tile_position=[1, 1],
            io_type="output",
        )
        self.assertEqual(
            underground_belt.to_dict(),
            {
                "name": "underground-belt",
                "position": {"x": 1.5, "y": 1.5},
                "direction": 2,
                "type": "output",
            },
        )

        # Warnings
        with self.assertWarns(DraftsmanWarning):
            UndergroundBelt(
                position=[0, 0], direction=Direction.WEST, invalid_keyword=5
            )

        # Errors
        # Raises InvalidEntityID when not in containers
        with self.assertRaises(InvalidEntityError):
            UndergroundBelt("this is not an underground belt")

        # Raises schema errors when any of the associated data is incorrect
        with self.assertRaises(TypeError):
            UndergroundBelt("underground-belt", id=25)

        with self.assertRaises(TypeError):
            UndergroundBelt("underground-belt", position=TypeError)

        with self.assertRaises(ValueError):
            UndergroundBelt("underground-belt", direction="incorrect")

        with self.assertRaises(ValueError):
            UndergroundBelt("underground-belt", io_type="incorrect")

    def test_power_and_circuit_flags(self):
        for name in underground_belts:
            underground_belt = UndergroundBelt(name)
            self.assertEqual(underground_belt.power_connectable, False)
            self.assertEqual(underground_belt.dual_power_connectable, False)
            self.assertEqual(underground_belt.circuit_connectable, False)
            self.assertEqual(underground_belt.dual_circuit_connectable, False)
