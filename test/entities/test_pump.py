# test_pump.py

from draftsman.entity import Pump, pumps
from draftsman.error import InvalidEntityError
from draftsman.warning import DraftsmanWarning

from unittest import TestCase

class PumpTesting(TestCase):
    def test_constructor_init(self):
        #loader = Loader()

        # Warnings
        with self.assertWarns(DraftsmanWarning):
            Pump("pump", unused_keyword = 10)

        # Errors
        with self.assertRaises(InvalidEntityError):
            Pump("this is not a pump")