# test_pipe.py

from draftsman.entity import Pipe, pipes
from draftsman.errors import InvalidEntityID

from unittest import TestCase

class PipeTesting(TestCase):
    def test_default_constructor(self):
        pipe = Pipe()
        self.assertEqual(
            pipe.to_dict(),
            {
                "name": "pipe",
                "position": {"x": 0.5, "y": 0.5}
            }
        )

    def test_constructor_init(self):
        #loader = Loader()

        # Warnings
        with self.assertWarns(UserWarning):
            Pipe("pipe", unused_keyword = 10)

        # Errors
        with self.assertRaises(InvalidEntityID):
            Pipe("Ceci n'est pas une pipe.")
