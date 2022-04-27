# test_pump.py
# -*- encoding: utf-8 -*-

from __future__ import unicode_literals

from draftsman.entity import Pump, pumps
from draftsman.error import InvalidEntityError
from draftsman.warning import DraftsmanWarning

import sys

if sys.version_info >= (3, 3):  # pragma: no coverage
    from unittest import TestCase
else:  # pragma: no coverage
    from unittest2 import TestCase


class PumpTesting(TestCase):
    def test_constructor_init(self):
        # loader = Loader()

        # Warnings
        with self.assertWarns(DraftsmanWarning):
            Pump("pump", unused_keyword=10)

        # Errors
        with self.assertRaises(InvalidEntityError):
            Pump("this is not a pump")
