# version.py

import draftsman

import unittest

class ValidateVersion(unittest.TestCase):
    def test_versions(self):
        self.assertEqual(draftsman.__version__, "0.3.5")
        self.assertEqual(draftsman.__version_info__, (0, 3, 5))