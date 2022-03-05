# test_boiler.py

from draftsman.entity import Boiler, boilers
from draftsman.errors import InvalidEntityID

from unittest import TestCase

class BoilerTesting(TestCase):
    def test_default_constructor(self):
        boiler = Boiler()
        self.assertEqual(
            boiler.to_dict(),
            {
                "name": "boiler",
                "position": {"x": 1.5, "y": 1.0}
            }
        )

    def test_constructor_init(self):
        boiler = Boiler()

        # Warnings
        with self.assertWarns(UserWarning):
            Boiler(unused_keyword = "whatever")

        # Errors
        with self.assertRaises(InvalidEntityID):
            Boiler("not a boiler")