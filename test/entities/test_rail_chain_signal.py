# test_rail_chain_signal.py
# -*- encoding: utf-8 -*-

from __future__ import unicode_literals

from draftsman.entity import RailChainSignal, rail_chain_signals
from draftsman.error import InvalidEntityError, InvalidSignalError, DataFormatError
from draftsman.warning import DraftsmanWarning

import sys

if sys.version_info >= (3, 3):  # pragma: no coverage
    import unittest
else:  # pragma: no coverage
    import unittest2 as unittest


class RailChainSignalTesting(unittest.TestCase):
    def test_constructor_init(self):
        rail_signal = RailChainSignal("rail-chain-signal", control_behavior={})
        self.assertEqual(
            rail_signal.to_dict(),
            {
                "name": "rail-chain-signal",
                "position": {"x": 0.5, "y": 0.5},
            },
        )

        rail_signal = RailChainSignal(
            "rail-chain-signal",
            control_behavior={
                "red_output_signal": "signal-A",
                "orange_output_signal": "signal-B",
                "green_output_signal": "signal-C",
                "blue_output_signal": "signal-D",
            },
        )
        self.assertEqual(
            rail_signal.to_dict(),
            {
                "name": "rail-chain-signal",
                "position": {"x": 0.5, "y": 0.5},
                "control_behavior": {
                    "red_output_signal": {"name": "signal-A", "type": "virtual"},
                    "orange_output_signal": {"name": "signal-B", "type": "virtual"},
                    "green_output_signal": {"name": "signal-C", "type": "virtual"},
                    "blue_output_signal": {"name": "signal-D", "type": "virtual"},
                },
            },
        )

        rail_signal = RailChainSignal(
            "rail-chain-signal",
            control_behavior={
                "red_output_signal": {"name": "signal-A", "type": "virtual"},
                "orange_output_signal": {"name": "signal-B", "type": "virtual"},
                "green_output_signal": {"name": "signal-C", "type": "virtual"},
                "blue_output_signal": {"name": "signal-D", "type": "virtual"},
            },
        )
        self.assertEqual(
            rail_signal.to_dict(),
            {
                "name": "rail-chain-signal",
                "position": {"x": 0.5, "y": 0.5},
                "control_behavior": {
                    "red_output_signal": {"name": "signal-A", "type": "virtual"},
                    "orange_output_signal": {"name": "signal-B", "type": "virtual"},
                    "green_output_signal": {"name": "signal-C", "type": "virtual"},
                    "blue_output_signal": {"name": "signal-D", "type": "virtual"},
                },
            },
        )

        # Warnings:
        with self.assertWarns(DraftsmanWarning):
            RailChainSignal("rail-chain-signal", invalid_keyword="whatever")

        # Warn if the rail signal is not placed next to rail
        # TODO (Complex)

        # Errors:
        with self.assertRaises(InvalidEntityError):
            RailChainSignal("this is not a rail chain signal")
        with self.assertRaises(DataFormatError):
            RailChainSignal(control_behavior={"unused_key": "something"})

    def test_set_blue_output_signal(self):
        rail_signal = RailChainSignal()
        rail_signal.blue_output_signal = "signal-A"
        self.assertEqual(
            rail_signal.blue_output_signal, {"name": "signal-A", "type": "virtual"}
        )
        self.assertEqual(
            rail_signal.control_behavior,
            {"blue_output_signal": {"name": "signal-A", "type": "virtual"}},
        )
        rail_signal.blue_output_signal = {"name": "signal-A", "type": "virtual"}
        self.assertEqual(
            rail_signal.control_behavior,
            {"blue_output_signal": {"name": "signal-A", "type": "virtual"}},
        )
        rail_signal.blue_output_signal = None
        self.assertEqual(rail_signal.control_behavior, {})
        with self.assertRaises(TypeError):
            rail_signal.blue_output_signal = TypeError
        with self.assertRaises(InvalidSignalError):
            rail_signal.blue_output_signal = "incorrect"

    def test_mergable_with(self):
        signal1 = RailChainSignal("rail-chain-signal")
        signal2 = RailChainSignal(
            "rail-chain-signal",
            control_behavior={
                "red_output_signal": "signal-A",
                "orange_output_signal": "signal-B",
                "green_output_signal": "signal-C",
                "blue_output_signal": "signal-D",
            },
            tags={"some": "stuff"},
        )

        self.assertTrue(signal1.mergable_with(signal1))

        self.assertTrue(signal1.mergable_with(signal2))
        self.assertTrue(signal2.mergable_with(signal1))

        signal2.tile_position = (1, 1)
        self.assertFalse(signal1.mergable_with(signal2))

    def test_merge(self):
        signal1 = RailChainSignal("rail-chain-signal")
        signal2 = RailChainSignal(
            "rail-chain-signal",
            control_behavior={
                "red_output_signal": "signal-A",
                "orange_output_signal": "signal-B",
                "green_output_signal": "signal-C",
                "blue_output_signal": "signal-D",
            },
            tags={"some": "stuff"},
        )

        signal1.merge(signal2)
        del signal2

        self.assertEqual(
            signal1.control_behavior,
            {
                "red_output_signal": {"name": "signal-A", "type": "virtual"},
                "orange_output_signal": {"name": "signal-B", "type": "virtual"},
                "green_output_signal": {"name": "signal-C", "type": "virtual"},
                "blue_output_signal": {"name": "signal-D", "type": "virtual"},
            },
        )
        self.assertEqual(signal1.tags, {"some": "stuff"})
