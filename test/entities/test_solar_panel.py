# test_solar_panel.py
# -*- encoding: utf-8 -*-

from __future__ import unicode_literals

from draftsman.entity import SolarPanel, solar_panels
from draftsman.error import InvalidEntityError
from draftsman.warning import DraftsmanWarning

import sys

if sys.version_info >= (3, 3):  # pragma: no coverage
    import unittest
else:  # pragma: no coverage
    import unittest2 as unittest


class SolarPanelTesting(unittest.TestCase):
    def test_constructor_init(self):
        solar_panel = SolarPanel()

        # Warnings
        with self.assertWarns(DraftsmanWarning):
            SolarPanel(unused_keyword="whatever")

        # Errors
        with self.assertRaises(InvalidEntityError):
            SolarPanel("not a solar_panel")
