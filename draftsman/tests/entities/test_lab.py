# test_lab.py
# -*- encoding: utf-8 -*-

from __future__ import unicode_literals

from draftsman.entity import Lab, labs
from draftsman.error import InvalidEntityError
from draftsman.warning import DraftsmanWarning

import sys

if sys.version_info >= (3, 3):  # pragma: no coverage
    from unittest import TestCase
else:  # pragma: no coverage
    from unittest2 import TestCase


class LabTesting(TestCase):
    def test_contstructor_init(self):
        lab = Lab()

        with self.assertWarns(DraftsmanWarning):
            Lab(unused_keyword="whatever")

        with self.assertRaises(InvalidEntityError):
            Lab("this is not a lab")
