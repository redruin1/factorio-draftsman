# test_underground_pipe.py

from draftsman.entity import UndergroundPipe, underground_pipes
from draftsman.errors import InvalidEntityID

from unittest import TestCase

class UndergroundPipeTesting(TestCase):
    def test_default_constructor(self):
        pipe = UndergroundPipe()
        self.assertEqual(
            pipe.to_dict(),
            {
                "name": "pipe-to-ground",
                "position": {"x": 0.5, "y": 0.5}
            }
        )

    def test_constructor_init(self):
        #loader = Loader()

        # Warnings
        with self.assertWarns(UserWarning):
            UndergroundPipe("pipe-to-ground", unused_keyword = 10)

        # Errors
        with self.assertRaises(InvalidEntityID):
            UndergroundPipe("this is not an underground pipe")