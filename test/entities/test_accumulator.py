# test_accumulator.py

from draftsman.entity import Accumulator, accumulators
from draftsman.errors import InvalidEntityID, InvalidSignalID

from schema import SchemaError

from unittest import TestCase

class AccumulatorTesting(TestCase):
    def test_default_constructor(self):
        accumulator = Accumulator()
        self.assertEqual(
            accumulator.to_dict(),
            {
                "name": "accumulator",
                "position": {"x": 1.0, "y": 1.0}
            }
        )

    def test_constructor_init(self):
        accumulator = Accumulator(
            control_behavior = {
                "output_signal": "signal-A"
            }
        )
        self.assertEqual(
            accumulator.to_dict(),
            {
                "name": "accumulator",
                "position": {"x": 1.0, "y": 1.0},
                "control_behavior": {
                    "output_signal": {
                        "name": "signal-A",
                        "type": "virtual"
                    }
                }
            }
        )
        accumulator = Accumulator(
            control_behavior = {
                "output_signal": {
                    "name": "signal-A",
                    "type": "virtual"
                }
            }
        )
        self.assertEqual(
            accumulator.to_dict(),
            {
                "name": "accumulator",
                "position": {"x": 1.0, "y": 1.0},
                "control_behavior": {
                    "output_signal": {
                        "name": "signal-A",
                        "type": "virtual"
                    }
                }
            }
        )

        # Warnings
        with self.assertWarns(UserWarning):
            Accumulator(unused_keyword = "whatever")

        # Errors
        with self.assertRaises(InvalidEntityID):
            Accumulator("not an accumulator")
        with self.assertRaises(SchemaError):
            Accumulator(control_behavior = {"output_signal": "incorrect"})

    def test_output_signal(self):
        accumulator = Accumulator()
        accumulator.set_output_signal("signal-D")
        self.assertEqual(
            accumulator.control_behavior,
            {
                "output_signal": {
                    "name": "signal-D",
                    "type": "virtual"
                }
            }
        )
        accumulator.set_output_signal(None)
        self.assertEqual(accumulator.control_behavior, {})
        with self.assertRaises(InvalidSignalID):
            accumulator.set_output_signal("incorrect")