# test_furnace.py

from draftsman.entity import Furnace, furnaces
from draftsman.error import InvalidEntityError
from draftsman.warning import DraftsmanWarning

from unittest import TestCase

class FurnaceTesting(TestCase):
    def test_constructor_init(self):
        furance = Furnace()

        # Warnings
        with self.assertWarns(DraftsmanWarning):
            Furnace(unused_keyword = "whatever")

        # Errors
        with self.assertRaises(InvalidEntityError):
            Furnace("not a heat pipe")