# test_boiler.py
# -*- encoding: utf-8 -*-

from __future__ import unicode_literals

from draftsman.entity import Boiler, boilers
from draftsman.error import InvalidEntityError
from draftsman.warning import DraftsmanWarning

import sys

if sys.version_info >= (3, 3):  # pragma: no coverage
    import unittest
else:  # pragma: no coverage
    import unittest2 as unittest


class BoilerTesting(unittest.TestCase):
    def test_constructor_init(self):
        boiler = Boiler()

        # Warnings
        with self.assertWarns(DraftsmanWarning):
            Boiler(unused_keyword="whatever")

        # Errors
        with self.assertRaises(InvalidEntityError):
            Boiler("not a boiler")
