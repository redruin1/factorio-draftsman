# test_heat_pipe.py
# -*- encoding: utf-8 -*-

from __future__ import unicode_literals

from draftsman.entity import HeatPipe, heat_pipes
from draftsman.error import InvalidEntityError
from draftsman.warning import DraftsmanWarning

import sys

if sys.version_info >= (3, 3):  # pragma: no coverage
    import unittest
else:  # pragma: no coverage
    import unittest2 as unittest


class HeatPipeTesting(unittest.TestCase):
    def test_constructor_init(self):
        heat_pipe = HeatPipe()

        # Warnings
        with self.assertWarns(DraftsmanWarning):
            HeatPipe(unused_keyword="whatever")

        # Errors
        with self.assertRaises(InvalidEntityError):
            HeatPipe("not a heat pipe")
