# test_offshore_pump.py
# -*- encoding: utf-8 -*-

from __future__ import unicode_literals

from draftsman.entity import OffshorePump, offshore_pumps
from draftsman.error import InvalidEntityError
from draftsman.warning import DraftsmanWarning

import sys

if sys.version_info >= (3, 3):  # pragma: no coverage
    from unittest import TestCase
else:  # pragma: no coverage
    from unittest2 import TestCase


class OffshorePumpTesting(TestCase):
    def test_constructor_init(self):
        pump = OffshorePump()

        # Warnings
        with self.assertWarns(DraftsmanWarning):
            OffshorePump(unused_keyword="whatever")

        # Errors
        with self.assertRaises(InvalidEntityError):
            OffshorePump("not a heat pipe")
