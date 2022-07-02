# test_accumulator.py
# -*- encoding: utf-8 -*-

from __future__ import unicode_literals

from draftsman.entity import Accumulator, accumulators, Container
from draftsman.error import InvalidEntityError, InvalidSignalError, DataFormatError
from draftsman.warning import DraftsmanWarning

from schema import SchemaError

import sys

if sys.version_info >= (3, 3):  # pragma: no coverage
    import unittest
else:  # pragma: no coverage
    import unittest2 as unittest


class AccumulatorTesting(unittest.TestCase):
    def test_constructor_init(self):
        accumulator = Accumulator(control_behavior={"output_signal": "signal-A"})
        self.assertEqual(
            accumulator.to_dict(),
            {
                "name": accumulators[0],
                "position": accumulator.position,
                "control_behavior": {
                    "output_signal": {"name": "signal-A", "type": "virtual"}
                },
            },
        )
        accumulator = Accumulator(
            control_behavior={"output_signal": {"name": "signal-A", "type": "virtual"}}
        )
        self.assertEqual(
            accumulator.to_dict(),
            {
                "name": accumulators[0],
                "position": accumulator.position,
                "control_behavior": {
                    "output_signal": {"name": "signal-A", "type": "virtual"}
                },
            },
        )

        # Warnings
        with self.assertWarns(DraftsmanWarning):
            Accumulator(unused_keyword="whatever")

        # Errors
        with self.assertRaises(InvalidEntityError):
            Accumulator("not an accumulator")
        with self.assertRaises(DataFormatError):
            Accumulator(control_behavior={"output_signal": "incorrect"})

    def test_output_signal(self):
        accumulator = Accumulator()
        # String case
        accumulator.output_signal = "signal-D"
        self.assertEqual(
            accumulator.output_signal, {"name": "signal-D", "type": "virtual"}
        )
        self.assertEqual(
            accumulator.control_behavior,
            {"output_signal": {"name": "signal-D", "type": "virtual"}},
        )
        # Dict case
        accumulator2 = Accumulator()
        accumulator2.output_signal = accumulator.output_signal
        self.assertEqual(accumulator2.output_signal, accumulator.output_signal)
        self.assertEqual(
            accumulator2.control_behavior,
            {"output_signal": {"name": "signal-D", "type": "virtual"}},
        )

        # None case
        accumulator.output_signal = None
        self.assertEqual(accumulator.control_behavior, {})
        with self.assertRaises(InvalidSignalError):
            accumulator.output_signal = "incorrect"
        with self.assertRaises(DataFormatError):
            accumulator.output_signal = {"incorrectly": "formatted"}

    def test_mergable(self):
        accumulatorA = Accumulator(
            "accumulator", 
            tile_position = (0, 0)
        )
        accumulatorB = Accumulator(
            "accumulator",
            tile_position = (0, 0)
        )
        
        # Compatible
        self.assertEqual(accumulatorA.mergable_with(accumulatorB), True)

        accumulatorA.output_signal = "signal-A"
        self.assertEqual(accumulatorA.mergable_with(accumulatorB), True)

        # Incompatible
        self.assertEqual(accumulatorA.mergable_with(Container()), False)

        accumulatorA.tile_position = (2, 0)
        self.assertEqual(accumulatorA.mergable_with(accumulatorB), False)

        accumulatorA.tile_position = (0, 0)
        accumulatorA.id = "something"
        self.assertEqual(accumulatorA.mergable_with(accumulatorB), False)

    def test_merge(self):
        accumulatorA = Accumulator(
            "accumulator", 
            tile_position = (0, 0)
        )
        accumulatorB = Accumulator(
            "accumulator",
            tile_position = (0, 0)
        )
        accumulatorB.output_signal = "signal-A"

        accumulatorA.merge(accumulatorB)
        self.assertEqual(accumulatorA.name, "accumulator")
        self.assertEqual(accumulatorA.tile_position, {"x": 0, "y": 0})
        self.assertEqual(
            accumulatorA.output_signal, {"name": "signal-A", "type": "virtual"}
        )
