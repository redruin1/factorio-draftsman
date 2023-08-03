# test_solar_panel.py
# -*- encoding: utf-8 -*-

from __future__ import unicode_literals

from draftsman.entity import SolarPanel, solar_panels
from draftsman.error import InvalidEntityError
from draftsman.warning import DraftsmanWarning

import sys
import pytest

if sys.version_info >= (3, 3):  # pragma: no coverage
    import unittest
else:  # pragma: no coverage
    import unittest2 as unittest


class SolarPanelTesting(unittest.TestCase):
    def test_constructor_init(self):
        solar_panel = SolarPanel()

        # Warnings
        with pytest.warns(DraftsmanWarning):
            SolarPanel(unused_keyword="whatever")

        # Errors
        with pytest.raises(InvalidEntityError):
            SolarPanel("not a solar_panel")

    def test_mergable_with(self):
        panel1 = SolarPanel("solar-panel")
        panel2 = SolarPanel("solar-panel", tags={"some": "stuff"})

        assert panel1.mergable_with(panel1)

        assert panel1.mergable_with(panel2)
        assert panel2.mergable_with(panel1)

        panel2.tile_position = (1, 1)
        assert not panel1.mergable_with(panel2)

    def test_merge(self):
        panel1 = SolarPanel("solar-panel")
        panel2 = SolarPanel("solar-panel", tags={"some": "stuff"})

        panel1.merge(panel2)
        del panel2

        assert panel1.tags == {"some": "stuff"}
