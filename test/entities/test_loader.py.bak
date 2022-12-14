# test_loader.py
# -*- encoding: utf-8 -*-

from __future__ import unicode_literals

from draftsman.entity import Loader, loaders
from draftsman.error import InvalidEntityError
from draftsman.warning import DraftsmanWarning

import sys

if sys.version_info >= (3, 3):  # pragma: no coverage
    import unittest
else:  # pragma: no coverage
    import unittest2 as unittest


class LoaderTesting(unittest.TestCase):
    def test_constructor_init(self):
        # loader = Loader()

        # Warnings
        with self.assertWarns(DraftsmanWarning):
            Loader("loader", unused_keyword=10)

        # Errors
        with self.assertRaises(InvalidEntityError):
            Loader("this is not a loader")

    def test_mergable_with(self):
        container1 = Loader()
        container2 = Loader(
            filters=[{"name": "coal", "index": 1}],
            io_type="input",
            tags={"some": "stuff"},
        )

        self.assertTrue(container1.mergable_with(container1))

        self.assertTrue(container1.mergable_with(container2))
        self.assertTrue(container2.mergable_with(container1))

        container2.tile_position = (1, 1)
        self.assertFalse(container1.mergable_with(container2))

    def test_merge(self):
        container1 = Loader()
        container2 = Loader(
            filters=[{"name": "coal", "index": 1}],
            io_type="input",
            tags={"some": "stuff"},
        )

        container1.merge(container2)
        del container2

        self.assertEqual(container1.filters, [{"name": "coal", "index": 1}])
        self.assertEqual(container1.io_type, "input")
        self.assertEqual(container1.tags, {"some": "stuff"})
