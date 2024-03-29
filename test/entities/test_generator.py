# test_generator.py
# -*- encoding: utf-8 -*-

from __future__ import unicode_literals

from draftsman.entity import Generator, generators
from draftsman.error import InvalidEntityError
from draftsman.warning import DraftsmanWarning

import sys

if sys.version_info >= (3, 3):  # pragma: no coverage
    import unittest
else:  # pragma: no coverage
    import unittest2 as unittest


class GeneratorTesting(unittest.TestCase):
    def test_constructor_init(self):
        generator = Generator("steam-engine")

        # Warnings
        with self.assertWarns(DraftsmanWarning):
            Generator("steam-engine", unused_keyword="whatever")

        # Errors
        with self.assertRaises(InvalidEntityError):
            Generator("not a generator")

    def test_mergable_with(self):
        gen1 = Generator("steam-engine")
        gen2 = Generator("steam-engine", tags={"some": "stuff"})

        self.assertTrue(gen1.mergable_with(gen1))

        self.assertTrue(gen1.mergable_with(gen2))
        self.assertTrue(gen2.mergable_with(gen1))

        gen2.tile_position = (10, 10)
        self.assertFalse(gen1.mergable_with(gen2))

    def test_merge(self):
        gen1 = Generator("steam-engine")
        gen2 = Generator("steam-engine", tags={"some": "stuff"})

        gen1.merge(gen2)
        del gen2

        self.assertEqual(gen1.tags, {"some": "stuff"})
