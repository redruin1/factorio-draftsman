# version.py
# -*- encoding: utf-8 -*-

import draftsman

import sys

if sys.version_info >= (3, 3):  # pragma: no coverage
    import unittest
else:  # pragma: no coverage
    import unittest2 as unittest


class ValidateVersion(unittest.TestCase):
    def test_versions(self):
        self.assertEqual(draftsman.__version__, "0.9.5")
        self.assertEqual(draftsman.__version_info__, (0, 9, 5))
