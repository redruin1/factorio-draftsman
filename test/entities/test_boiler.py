# test_boiler.py

from draftsman.entity import Boiler, boilers
from draftsman.error import InvalidEntityError
from draftsman.warning import DraftsmanWarning

from unittest import TestCase

class BoilerTesting(TestCase):
    def test_constructor_init(self):
        boiler = Boiler()

        # Warnings
        with self.assertWarns(DraftsmanWarning):
            Boiler(unused_keyword = "whatever")

        # Errors
        with self.assertRaises(InvalidEntityError):
            Boiler("not a boiler")