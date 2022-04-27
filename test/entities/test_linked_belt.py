# test_linked_belt.py
# -*- encoding: utf-8 -*-

from __future__ import unicode_literals

from draftsman.entity import LinkedBelt, linked_belts
from draftsman.error import InvalidEntityError
from draftsman.warning import DraftsmanWarning

import sys

if sys.version_info >= (3, 3):  # pragma: no coverage
    from unittest import TestCase
else:  # pragma: no coverage
    from unittest2 import TestCase


class LinkedBeltTesting(TestCase):
    def test_constructor_init(self):
        linked_belt = LinkedBelt()

        # Warnings
        with self.assertWarns(DraftsmanWarning):
            LinkedBelt(unused_keyword="whatever")

        # Errors
        with self.assertRaises(InvalidEntityError):
            LinkedBelt("this is not a linked belt")
