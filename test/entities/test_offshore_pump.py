# test_offshore_pump.py

from draftsman.entity import OffshorePump, offshore_pumps
from draftsman.error import InvalidEntityError
from draftsman.warning import DraftsmanWarning

from unittest import TestCase

class OffshorePumpTesting(TestCase):
    def test_constructor_init(self):
        pump = OffshorePump()

        # Warnings
        with self.assertWarns(DraftsmanWarning):
            OffshorePump(unused_keyword = "whatever")

        # Errors
        with self.assertRaises(InvalidEntityError):
            OffshorePump("not a heat pipe")