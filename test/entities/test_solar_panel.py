# test_solar_panel.py

from draftsman.entity import SolarPanel, solar_panels
from draftsman.error import InvalidEntityError
from draftsman.warning import DraftsmanWarning

from unittest import TestCase

class SolarPanelTesting(TestCase):
    def test_constructor_init(self):
        solar_panel = SolarPanel()

        # Warnings
        with self.assertWarns(DraftsmanWarning):
            SolarPanel(unused_keyword = "whatever")

        # Errors
        with self.assertRaises(InvalidEntityError):
            SolarPanel("not a solar_panel")