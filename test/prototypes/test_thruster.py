# test_thruster.py

from draftsman import DEFAULT_FACTORIO_VERSION
from draftsman.data import mods
from draftsman.prototypes.thruster import (
    Thruster,
    thrusters,
)
from draftsman.warning import UnknownEntityWarning

import pytest


@pytest.fixture
def valid_thruster():
    if len(thrusters) == 0:
        return None
    return Thruster(
        "thruster",
        id="test",
        quality="uncommon",
        tile_position=(1, 1),
        tags={"blah": "blah"},
    )


@pytest.mark.skipif(len(thrusters) == 0, reason="No Thrusters to test")
class TestThruster:
    def test_constructor(self):
        thruster = Thruster("thruster")

        with pytest.warns(UnknownEntityWarning):
            Thruster("unknown thruster")

    def test_flags(self):
        for thruster_name in thrusters:
            thruster = Thruster(thruster_name)
            assert thruster.power_connectable == False
            assert thruster.dual_power_connectable == False
            assert thruster.circuit_connectable == False
            assert thruster.dual_circuit_connectable == False

    def test_surface_conditions(self):
        thruster = Thruster("thruster")
        if mods.versions.get("base", DEFAULT_FACTORIO_VERSION) == (2, 0, 9, 0):
            assert thruster.surface_conditions == [{"property": "pressure", "max": 0}]
        else:
            assert thruster.surface_conditions == [
                {"property": "pressure", "max": 0, "min": 0}
            ]
        assert thruster.is_placable_on("nauvis") is False

        with pytest.warns(UnknownEntityWarning):
            thruster = Thruster("unknown thruster")
        assert thruster.surface_conditions is None
        assert thruster.is_placable_on("nauvis") is True

    # TODO: make a fixture for every entity
    # def test_eq():
    #     attractor1 = LightningAttractor("inserter")
    #     attractor2 = LightningAttractor("inserter")

    #     assert attractor1 == attractor2

    #     attractor1.tags = {"some": "stuff"}

    #     assert attractor1 != attractor2

    #     container = Container()

    #     assert attractor1 != container
    #     assert attractor2 != container

    #     # hashable
    #     assert isinstance(attractor1, Hashable)
