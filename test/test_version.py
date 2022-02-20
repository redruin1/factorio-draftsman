# version.py

import factoriotools

import unittest

class ValidateVersion(unittest.TestCase):
    def test_versions(self):
        self.assertEqual(factoriotools.__version__, "0.1")
        self.assertEqual(factoriotools.__version_info__, (0, 1))