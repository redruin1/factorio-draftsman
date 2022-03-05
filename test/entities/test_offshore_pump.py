# test_offshore_pump.py

from draftsman.entity import OffshorePump, offshore_pumps
from draftsman.errors import InvalidEntityID

from unittest import TestCase

class OffshorePumpTesting(TestCase):
    def test_default_constructor(self):
        pump = OffshorePump()
        self.assertEqual(
            pump.to_dict(),
            {
                "name": "offshore-pump",
                "position": {"x": 0.5, "y": 0.5} # special item, actually 1x1
            }
        )

    def test_constructor_init(self):
        pump = OffshorePump()

        # Warnings
        with self.assertWarns(UserWarning):
            OffshorePump(unused_keyword = "whatever")

        # Errors
        with self.assertRaises(InvalidEntityID):
            OffshorePump("not a heat pipe")