# test_furnace.py

from draftsman.entity import Furnace, furnaces
from draftsman.errors import InvalidEntityID

from unittest import TestCase

class FurnaceTesting(TestCase):
    def test_default_constructor(self):
        furnace = Furnace()
        self.assertEqual(
            furnace.to_dict(),
            {
                "name": "stone-furnace",
                "position": {"x": 1.0, "y": 1.0}
            }
        )

    def test_constructor_init(self):
        furance = Furnace()

        # Warnings
        with self.assertWarns(UserWarning):
            Furnace(unused_keyword = "whatever")

        # Errors
        with self.assertRaises(InvalidEntityID):
            Furnace("not a heat pipe")