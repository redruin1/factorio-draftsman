# test_offshore_pump.py
# -*- encoding: utf-8 -*-

from __future__ import unicode_literals

from draftsman.entity import OffshorePump, offshore_pumps
from draftsman.error import InvalidEntityError, DataFormatError
from draftsman.warning import DraftsmanWarning

import sys

if sys.version_info >= (3, 3):  # pragma: no coverage
    import unittest
else:  # pragma: no coverage
    import unittest2 as unittest


class OffshorePumpTesting(unittest.TestCase):
    def test_constructor_init(self):
        pump = OffshorePump()

        # Warnings
        with self.assertWarns(DraftsmanWarning):
            OffshorePump(unused_keyword="whatever")

        # Errors
        with self.assertRaises(InvalidEntityError):
            OffshorePump("not a heat pipe")
        with self.assertRaises(DataFormatError):
            OffshorePump(control_behavior={"unused_key": "something"})

    def test_mergable_with(self):
        pump1 = OffshorePump("offshore-pump")
        pump2 = OffshorePump("offshore-pump", tags={"some": "stuff"})

        self.assertTrue(pump1.mergable_with(pump1))

        self.assertTrue(pump1.mergable_with(pump2))
        self.assertTrue(pump2.mergable_with(pump1))

        pump2.tile_position = (1, 1)
        self.assertFalse(pump1.mergable_with(pump2))

    def test_merge(self):
        pump1 = OffshorePump("offshore-pump")
        pump2 = OffshorePump("offshore-pump", tags={"some": "stuff"})

        pump1.merge(pump2)
        del pump2

        self.assertEqual(pump1.tags, {"some": "stuff"})
