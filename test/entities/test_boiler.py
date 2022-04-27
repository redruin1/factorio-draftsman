# test_boiler.py
# -*- encoding: utf-8 -*-

from __future__ import unicode_literals

from draftsman.entity import Boiler, boilers
from draftsman.error import InvalidEntityError
from draftsman.warning import DraftsmanWarning

import sys

if sys.version_info >= (3, 3):  # pragma: no coverage
    from unittest import TestCase
else:  # pragma: no coverage
    from unittest2 import TestCase


class BoilerTesting(TestCase):
    def test_constructor_init(self):
        boiler = Boiler()

        # Warnings
        with self.assertWarns(DraftsmanWarning):
            Boiler(unused_keyword="whatever")

        # Errors
        with self.assertRaises(InvalidEntityError):
            Boiler("not a boiler")
