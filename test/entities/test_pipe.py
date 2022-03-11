# test_pipe.py

from draftsman.entity import Pipe, pipes
from draftsman.error import InvalidEntityError
from draftsman.warning import DraftsmanWarning

from unittest import TestCase

class PipeTesting(TestCase):
    def test_constructor_init(self):
        #loader = Loader()

        # Warnings
        with self.assertWarns(DraftsmanWarning):
            Pipe("pipe", unused_keyword = 10)

        # Errors
        with self.assertRaises(InvalidEntityError):
            Pipe("Ceci n'est pas une pipe.")
