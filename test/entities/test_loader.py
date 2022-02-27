# test_loader.py

from draftsman.entity import Loader, loaders
from draftsman.errors import InvalidEntityID

from unittest import TestCase

class LoaderTesting(TestCase):
    def test_default_constructor(self):
        loader = Loader()
        self.assertEqual(
            loader.to_dict(),
            {
                "name": "loader",
                "position": {"x": 0.5, "y": 1.0}
            }
        )

    def test_constructor_init(self):
        #loader = Loader()

        # Warnings
        with self.assertWarns(UserWarning):
            Loader("loader", unused_keyword = 10)

        # Errors
        with self.assertRaises(InvalidEntityID):
            Loader("this is not a loader")