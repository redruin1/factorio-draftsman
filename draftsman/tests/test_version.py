# version.py
# -*- encoding: utf-8 -*-

import draftsman

import sys

if sys.version_info >= (3, 3):  # pragma: no coverage
    from unittest import TestCase
else:  # pragma: no coverage
    from unittest2 import TestCase


class ValidateVersion(TestCase):
    def test_versions(self):
        self.assertEqual(draftsman.__version__, "0.6.0")
        self.assertEqual(draftsman.__version_info__, (0, 6, 0))
