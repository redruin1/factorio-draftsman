# test_rail_signal.py
# -*- encoding: utf-8 -*-

from __future__ import unicode_literals

from draftsman.entity import RailSignal, rail_signals
from draftsman.error import InvalidEntityError
from draftsman.warning import DraftsmanWarning

from schema import SchemaError

import sys

if sys.version_info >= (3, 3):  # pragma: no coverage
    from unittest import TestCase
else:  # pragma: no coverage
    from unittest2 import TestCase


class RailSignalTesting(TestCase):
    def test_constructor_init(self):
        rail_signal = RailSignal("rail-signal", control_behavior={})
        self.assertEqual(
            rail_signal.to_dict(),
            {
                "name": "rail-signal",
                "position": {"x": 0.5, "y": 0.5},
            },
        )

        rail_signal = RailSignal(
            "rail-signal",
            control_behavior={
                "red_output_signal": "signal-A",
                "yellow_output_signal": "signal-B",
                "green_output_signal": "signal-C",
            },
        )
        self.assertEqual(
            rail_signal.to_dict(),
            {
                "name": "rail-signal",
                "position": {"x": 0.5, "y": 0.5},
                "control_behavior": {
                    "red_output_signal": {"name": "signal-A", "type": "virtual"},
                    "yellow_output_signal": {"name": "signal-B", "type": "virtual"},
                    "green_output_signal": {"name": "signal-C", "type": "virtual"},
                },
            },
        )

        rail_signal = RailSignal(
            "rail-signal",
            control_behavior={
                "red_output_signal": {"name": "signal-A", "type": "virtual"},
                "yellow_output_signal": {"name": "signal-B", "type": "virtual"},
                "green_output_signal": {"name": "signal-C", "type": "virtual"},
            },
        )
        self.assertEqual(
            rail_signal.to_dict(),
            {
                "name": "rail-signal",
                "position": {"x": 0.5, "y": 0.5},
                "control_behavior": {
                    "red_output_signal": {"name": "signal-A", "type": "virtual"},
                    "yellow_output_signal": {"name": "signal-B", "type": "virtual"},
                    "green_output_signal": {"name": "signal-C", "type": "virtual"},
                },
            },
        )

        # Warnings:
        with self.assertWarns(DraftsmanWarning):
            RailSignal("rail-signal", invalid_keyword="whatever")
        # Warn if the rail signal is not placed next to rail
        # TODO (Complex)

        # Errors:
        with self.assertRaises(InvalidEntityError):
            RailSignal("this is not a rail signal")

    def test_read_signal(self):
        rail_signal = RailSignal()
        rail_signal.read_signal = True
        self.assertEqual(rail_signal.read_signal, True)
        self.assertEqual(rail_signal.control_behavior, {"circuit_read_signal": True})
        rail_signal.read_signal = None
        self.assertEqual(rail_signal.control_behavior, {})
        with self.assertRaises(TypeError):
            rail_signal.read_signal = "incorrect"

    def test_enable_disable(self):
        rail_signal = RailSignal()
        rail_signal.enable_disable = True
        self.assertEqual(rail_signal.enable_disable, True)
        self.assertEqual(rail_signal.control_behavior, {"circuit_close_signal": True})
        rail_signal.enable_disable = None
        self.assertEqual(rail_signal.control_behavior, {})
        with self.assertRaises(TypeError):
            rail_signal.enable_disable = "incorrect"
