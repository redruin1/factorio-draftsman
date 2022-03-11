# test_accumulator.py

from draftsman.entity import Accumulator, accumulators
from draftsman.error import InvalidEntityError, InvalidSignalError
from draftsman.warning import DraftsmanWarning

from schema import SchemaError

from unittest import TestCase

class AccumulatorTesting(TestCase):
    def test_constructor_init(self):
        accumulator = Accumulator(
            control_behavior = {
                "output_signal": "signal-A"
            }
        )
        self.assertEqual(
            accumulator.to_dict(),
            {
                "name": accumulators[0],
                "position": accumulator.position,
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
                "name": accumulators[0],
                "position": accumulator.position,
                "control_behavior": {
                    "output_signal": {
                        "name": "signal-A",
                        "type": "virtual"
                    }
                }
            }
        )

        # Warnings
        with self.assertWarns(DraftsmanWarning):
            Accumulator(unused_keyword = "whatever")

        # Errors
        with self.assertRaises(InvalidEntityError):
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
        with self.assertRaises(InvalidSignalError):
            accumulator.set_output_signal("incorrect")