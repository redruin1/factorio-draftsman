# test_solar_panel.py

from draftsman.entity import SolarPanel, solar_panels
from draftsman.errors import InvalidEntityID

from unittest import TestCase

class SolarPanelTesting(TestCase):
    def test_default_constructor(self):
        solar_panel = SolarPanel()
        self.assertEqual(
            solar_panel.to_dict(),
            {
                "name": "solar-panel",
                "position": {"x": 1.5, "y": 1.5}
            }
        )

    def test_constructor_init(self):
        solar_panel = SolarPanel()

        # Warnings
        with self.assertWarns(UserWarning):
            SolarPanel(unused_keyword = "whatever")

        # Errors
        with self.assertRaises(InvalidEntityID):
            SolarPanel("not a solar_panel")