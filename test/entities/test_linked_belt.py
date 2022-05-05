# test_linked_belt.py
# -*- encoding: utf-8 -*-

from __future__ import unicode_literals

from draftsman.entity import LinkedBelt, linked_belts
from draftsman.error import InvalidEntityError
from draftsman.warning import DraftsmanWarning

import sys

if sys.version_info >= (3, 3):  # pragma: no coverage
    import unittest
else:  # pragma: no coverage
    import unittest2 as unittest


# For compatibility with versions of Factorio prior to 1.1.6
@unittest.skipIf(len(linked_belts) == 0, "No linked belts to test")
class LinkedBeltTesting(unittest.TestCase):
    def test_constructor_init(self):
        linked_belt = LinkedBelt()

        # Warnings
        with self.assertWarns(DraftsmanWarning):
            LinkedBelt(unused_keyword="whatever")

        # Errors
        with self.assertRaises(InvalidEntityError):
            LinkedBelt("this is not a linked belt")
