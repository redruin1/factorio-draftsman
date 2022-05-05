# test_lab.py
# -*- encoding: utf-8 -*-

from __future__ import unicode_literals

from draftsman.entity import Lab, labs
from draftsman.error import InvalidEntityError
from draftsman.warning import DraftsmanWarning

import sys

if sys.version_info >= (3, 3):  # pragma: no coverage
    import unittest
else:  # pragma: no coverage
    import unittest2 as unittest


class LabTesting(unittest.TestCase):
    def test_contstructor_init(self):
        lab = Lab()

        with self.assertWarns(DraftsmanWarning):
            Lab(unused_keyword="whatever")

        with self.assertRaises(InvalidEntityError):
            Lab("this is not a lab")
