# test_heat_pipe.py

from draftsman.entity import HeatPipe, heat_pipes
from draftsman.error import InvalidEntityError
from draftsman.warning import DraftsmanWarning

from unittest import TestCase

class HeatPipeTesting(TestCase):
    def test_constructor_init(self):
        heat_pipe = HeatPipe()

        # Warnings
        with self.assertWarns(DraftsmanWarning):
            HeatPipe(unused_keyword = "whatever")

        # Errors
        with self.assertRaises(InvalidEntityError):
            HeatPipe("not a heat pipe")