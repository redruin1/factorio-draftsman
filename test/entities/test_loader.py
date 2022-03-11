# test_loader.py

from draftsman.entity import Loader, loaders
from draftsman.error import InvalidEntityError
from draftsman.warning import DraftsmanWarning

from unittest import TestCase

class LoaderTesting(TestCase):
    def test_constructor_init(self):
        #loader = Loader()

        # Warnings
        with self.assertWarns(DraftsmanWarning):
            Loader("loader", unused_keyword = 10)

        # Errors
        with self.assertRaises(InvalidEntityError):
            Loader("this is not a loader")