# test_underground_pipe.py

from draftsman.entity import UndergroundPipe, underground_pipes
from draftsman.error import InvalidEntityError
from draftsman.warning import DraftsmanWarning

from unittest import TestCase

class UndergroundPipeTesting(TestCase):
    def test_constructor_init(self):
        #loader = Loader()

        # Warnings
        with self.assertWarns(DraftsmanWarning):
            UndergroundPipe("pipe-to-ground", unused_keyword = 10)

        # Errors
        with self.assertRaises(InvalidEntityError):
            UndergroundPipe("this is not an underground pipe")