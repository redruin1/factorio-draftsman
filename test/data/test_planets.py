# test_planets.py

from draftsman.data import planets

import pytest

class TestPlanets:
    def test_unknown_surface_properties(self):
        assert planets.get_surface_properties("unknown") == {}

    @pytest.mark.skipif("nauvis" not in planets.raw, reason="'nauvis' planet not found")
    def test_get_surface_properties(self):
        assert planets.get_surface_properties("nauvis") == {
            "solar-power": 100,
            "magnetic-field": 90,
            "pressure": 1000,
            "gravity": 10,
        }