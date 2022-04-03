# test_heat_pipe.py
# -*- encoding: utf-8 -*-

from __future__ import unicode_literals

from draftsman.entity import HeatPipe, heat_pipes
from draftsman.error import InvalidEntityError
from draftsman.warning import DraftsmanWarning

import sys

if sys.version_info >= (3, 3):  # pragma: no coverage
    from unittest import TestCase
else:  # pragma: no coverage
    from unittest2 import TestCase


class HeatPipeTesting(TestCase):
    def test_constructor_init(self):
        heat_pipe = HeatPipe()

        # Warnings
        with self.assertWarns(DraftsmanWarning):
            HeatPipe(unused_keyword="whatever")

        # Errors
        with self.assertRaises(InvalidEntityError):
            HeatPipe("not a heat pipe")
