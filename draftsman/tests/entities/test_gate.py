# test_gate.py
# -*- encoding: utf-8 -*-

from __future__ import unicode_literals

from draftsman.entity import Gate, gates
from draftsman.error import InvalidEntityError
from draftsman.warning import DraftsmanWarning

import sys

if sys.version_info >= (3, 3):  # pragma: no coverage
    from unittest import TestCase
else:  # pragma: no coverage
    from unittest2 import TestCase


class GateTesting(TestCase):
    def test_contstructor_init(self):
        gate = Gate()

        with self.assertWarns(DraftsmanWarning):
            Gate(unused_keyword="whatever")

        with self.assertRaises(InvalidEntityError):
            Gate("this is not a gate")
