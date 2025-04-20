# test_solar_panel.py

from draftsman.entity import SolarPanel, solar_panels, Container
from draftsman.warning import UnknownEntityWarning, UnknownKeywordWarning

from collections.abc import Hashable
import pytest


class TestSolarPanel:
    def test_constructor_init(self):
        solar_panel = SolarPanel("solar-panel")
        assert solar_panel.to_dict() == {
            "name": "solar-panel",
            "position": {"x": 1.5, "y": 1.5},
        }

        # Warnings
        with pytest.warns(UnknownKeywordWarning):
            SolarPanel.from_dict(
                {"name": "solar-panel", "unused_keyword": "whatever"}
            ).validate().reissue_all()

        # Errors
        with pytest.warns(UnknownEntityWarning):
            SolarPanel("not a solar_panel").validate().reissue_all()

    def test_power_and_circuit_flags(self):
        for name in solar_panels:
            panel = SolarPanel(name)
            assert panel.power_connectable == False
            assert panel.dual_power_connectable == False
            assert panel.circuit_connectable == False
            assert panel.dual_circuit_connectable == False

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

    def test_eq(self):
        panel1 = SolarPanel("solar-panel")
        panel2 = SolarPanel("solar-panel")

        assert panel1 == panel2

        panel1.tags = {"some": "stuff"}

        assert panel1 != panel2

        container = Container()

        assert panel1 != container
        assert panel2 != container

        # hashable
        assert isinstance(panel1, Hashable)
