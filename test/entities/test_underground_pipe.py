# test_underground_pipe.py
# -*- encoding: utf-8 -*-

from __future__ import unicode_literals

from draftsman.entity import UndergroundPipe, underground_pipes
from draftsman.error import InvalidEntityError
from draftsman.warning import DraftsmanWarning

import sys

if sys.version_info >= (3, 3):  # pragma: no coverage
    import unittest
else:  # pragma: no coverage
    import unittest2 as unittest


class UndergroundPipeTesting(unittest.TestCase):
    def test_constructor_init(self):
        # loader = Loader()

        # Warnings
        with self.assertWarns(DraftsmanWarning):
            UndergroundPipe("pipe-to-ground", unused_keyword=10)

        # Errors
        with self.assertRaises(InvalidEntityError):
            UndergroundPipe("this is not an underground pipe")

    def test_mergable_with(self):
        pipe1 = UndergroundPipe("pipe-to-ground")
        pipe2 = UndergroundPipe("pipe-to-ground", tags={"some": "stuff"})

        self.assertTrue(pipe1.mergable_with(pipe1))

        self.assertTrue(pipe1.mergable_with(pipe2))
        self.assertTrue(pipe2.mergable_with(pipe1))

        pipe2.tile_position = (1, 1)
        self.assertFalse(pipe1.mergable_with(pipe2))

    def test_merge(self):
        pipe1 = UndergroundPipe("pipe-to-ground")
        pipe2 = UndergroundPipe("pipe-to-ground", tags={"some": "stuff"})

        pipe1.merge(pipe2)
        del pipe2

        self.assertEqual(pipe1.tags, {"some": "stuff"})
