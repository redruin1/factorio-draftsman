# test_thruster.py

from draftsman.prototypes.thruster import (
    Thruster,
    thrusters,
)
from draftsman.warning import UnknownEntityWarning

import pytest


def test_constructor():
    thruster = Thruster("thruster")

    with pytest.warns(UnknownEntityWarning):
        Thruster("unknown thruster")


def test_flags():
    for thruster_name in thrusters:
        thruster = Thruster(thruster_name)
        assert thruster.power_connectable == False
        assert thruster.dual_power_connectable == False
        assert thruster.circuit_connectable == False
        assert thruster.dual_circuit_connectable == False


def test_surface_conditions():
    thruster = Thruster("thruster")
    assert thruster.surface_conditions == [{"property": "pressure", "max": 0, "min": 0}]
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