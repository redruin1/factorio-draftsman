# test_wall.py
# -*- encoding: utf-8 -*-

from __future__ import unicode_literals

from draftsman.entity import Wall, walls
from draftsman.error import InvalidEntityError, InvalidSignalError
from draftsman.warning import DraftsmanWarning

from schema import SchemaError

import sys

if sys.version_info >= (3, 3):  # pragma: no coverage
    from unittest import TestCase
else:  # pragma: no coverage
    from unittest2 import TestCase


class WallTesting(TestCase):
    def test_contstructor_init(self):
        wall = Wall()

        with self.assertWarns(DraftsmanWarning):
            Wall(unused_keyword="whatever")

        with self.assertRaises(InvalidEntityError):
            Wall("this is not a wall")

    def test_set_enable_disable(self):
        wall = Wall()
        wall.enable_disable = True
        self.assertEqual(wall.enable_disable, True)
        self.assertEqual(wall.control_behavior, {"circuit_open_gate": True})
        wall.enable_disable = None
        self.assertEqual(wall.control_behavior, {})
        with self.assertRaises(TypeError):
            wall.enable_disable = "incorrect"

    def test_set_read_gate(self):
        wall = Wall()
        wall.read_gate = True
        self.assertEqual(wall.read_gate, True)
        self.assertEqual(wall.control_behavior, {"circuit_read_sensor": True})
        wall.read_gate = None
        self.assertEqual(wall.control_behavior, {})
        with self.assertRaises(TypeError):
            wall.read_gate = "incorrect"

    def test_set_output_signal(self):
        wall = Wall()
        wall.output_signal = "signal-A"
        self.assertEqual(wall.output_signal, {"name": "signal-A", "type": "virtual"})
        self.assertEqual(
            wall.control_behavior,
            {"output_signal": {"name": "signal-A", "type": "virtual"}},
        )
        wall.output_signal = {"name": "signal-A", "type": "virtual"}
        self.assertEqual(
            wall.control_behavior,
            {"output_signal": {"name": "signal-A", "type": "virtual"}},
        )
        wall.output_signal = None
        self.assertEqual(wall.control_behavior, {})
        with self.assertRaises(TypeError):
            wall.output_signal = TypeError
        with self.assertRaises(InvalidSignalError):
            wall.output_signal = "incorrect"
