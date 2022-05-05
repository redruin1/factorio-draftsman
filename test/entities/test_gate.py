# test_gate.py
# -*- encoding: utf-8 -*-

from __future__ import unicode_literals

from draftsman.entity import Gate, gates
from draftsman.error import InvalidEntityError
from draftsman.warning import DraftsmanWarning

import sys

if sys.version_info >= (3, 3):  # pragma: no coverage
    import unittest
else:  # pragma: no coverage
    import unittest2 as unittest


class GateTesting(unittest.TestCase):
    def test_contstructor_init(self):
        gate = Gate()

        with self.assertWarns(DraftsmanWarning):
            Gate(unused_keyword="whatever")

        with self.assertRaises(InvalidEntityError):
            Gate("this is not a gate")
