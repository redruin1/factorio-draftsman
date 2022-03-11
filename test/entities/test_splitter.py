# test_splitter.py

from draftsman.constants import Direction
from draftsman.entity import Splitter, splitters
from draftsman.error import InvalidEntityError
from draftsman.warning import DraftsmanWarning

from schema import SchemaError

from unittest import TestCase

class SplitterTesting(TestCase):
    def test_constructor_init(self):
        # Valid
        splitter = Splitter(
            "splitter", 
            direction = Direction.EAST,
            position = [1, 1],
            input_priority = "left",
            output_priority = "right",
            filter = "small-lamp"
        )
        self.assertEqual(
            splitter.to_dict(),
            {
                "name": "splitter",
                "position": {"x": 1.5, "y": 2.0},
                "direction": 2,
                "input_priority": "left",
                "output_priority": "right",
                "filter": "small-lamp"
            }
        )

        # Warnings
        with self.assertWarns(DraftsmanWarning):
            Splitter(
                position = [0, 0], direction = Direction.WEST, invalid_keyword = 5
            )

        # Errors
        # Raises InvalidEntityID when not in containers
        with self.assertRaises(InvalidEntityError):
            Splitter("this is not a splitter")

        # Raises schema errors when any of the associated data is incorrect
        with self.assertRaises(SchemaError):
            Splitter("splitter", id = 25)

        with self.assertRaises(SchemaError):
            Splitter("splitter", position = "invalid")
        
        with self.assertRaises(SchemaError):
            Splitter("splitter", direction = "incorrect")

        with self.assertRaises(ValueError): # maybe schema error?
            Splitter("splitter", input_priority = "wrong")

        with self.assertRaises(ValueError): # maybe schema error?
            Splitter("splitter", output_priority = "wrong")

        with self.assertRaises(ValueError): # maybe schema error?
            Splitter("splitter", filter = "wrong")

    def test_power_and_circuit_flags(self):
        for name in splitters:
            splitter = Splitter(name)
            self.assertEqual(splitter.power_connectable, False)
            self.assertEqual(splitter.dual_power_connectable, False)
            self.assertEqual(splitter.circuit_connectable, False)
            self.assertEqual(splitter.dual_circuit_connectable, False)