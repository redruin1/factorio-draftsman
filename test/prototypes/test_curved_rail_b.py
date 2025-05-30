# test_curved_rail_b.py

from draftsman.constants import Direction
from draftsman.prototypes.curved_rail_b import (
    CurvedRailB,
    curved_rails_b,
)
from draftsman.warning import UnknownEntityWarning

import pytest


@pytest.fixture
def valid_curved_rail_b():
    if len(curved_rails_b) == 0:
        return None
    return CurvedRailB(
        "curved-rail-b",
        id="test",
        quality="uncommon",
        tile_position=(2, 2),
        direction=Direction.EAST,
        tags={"blah": "blah"},
    )


def test_constructor():
    curved_rail = CurvedRailB("curved-rail-b")

    with pytest.warns(UnknownEntityWarning):
        CurvedRailB("unknown curved rail")


def test_flags():
    for rail_name in curved_rails_b:
        curved_rail = CurvedRailB(rail_name)
        assert curved_rail.power_connectable == False
        assert curved_rail.dual_power_connectable == False
        assert curved_rail.circuit_connectable == False
        assert curved_rail.dual_circuit_connectable == False
