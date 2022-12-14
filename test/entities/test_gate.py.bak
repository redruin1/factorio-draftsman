# test_gate.py
# -*- encoding: utf-8 -*-

from __future__ import unicode_literals

from draftsman.constants import Direction
from draftsman.entity import Gate, gates
from draftsman.error import InvalidEntityError
from draftsman.warning import DraftsmanWarning

import sys

if sys.version_info >= (3, 3):  # pragma: no coverage
    import unittest
else:  # pragma: no coverage
    import unittest2 as unittest


class GateTesting(unittest.TestCase):
    def test_contstructor_init(self):
        gate = Gate("gate")

        with self.assertWarns(DraftsmanWarning):
            Gate("gate", unused_keyword="whatever")

        with self.assertRaises(InvalidEntityError):
            Gate("this is not a gate")

    def test_mergable_with(self):
        gate1 = Gate("gate", tile_position=(1, 1))
        gate2 = Gate("gate", position=(1.5, 1.5), tags={"some": "stuff"})

        self.assertTrue(gate1.mergable_with(gate1))

        self.assertTrue(gate1.mergable_with(gate2))
        self.assertTrue(gate2.mergable_with(gate1))

        gate2.direction = Direction.EAST
        self.assertFalse(gate1.mergable_with(gate2))

    def test_merge(self):
        gate1 = Gate("gate", tile_position=(1, 1))
        gate2 = Gate("gate", position=(1.5, 1.5), tags={"some": "stuff"})

        gate1.merge(gate2)
        del gate2

        self.assertEqual(gate1.tags, {"some": "stuff"})
