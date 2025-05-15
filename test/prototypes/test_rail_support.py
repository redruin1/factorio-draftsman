# test_rail_support.py

from draftsman.prototypes.rail_support import (
    RailSupport,
    rail_supports,
)
from draftsman.warning import UnknownEntityWarning

import pytest


@pytest.fixture
def valid_rail_support():
    if len(rail_supports) == 0:
        return None
    return RailSupport(
        "rail-support",
        id="test",
        quality="uncommon",
        tile_position=(2, 2),
        tags={"blah": "blah"},
    )


def test_constructor():
    support = RailSupport("rail-support")

    with pytest.warns(UnknownEntityWarning):
        RailSupport("unknown rail support")


def test_flags():
    for support_name in rail_supports:
        support = RailSupport(support_name)
        assert support.power_connectable == False
        assert support.dual_power_connectable == False
        assert support.circuit_connectable == False
        assert support.dual_circuit_connectable == False
