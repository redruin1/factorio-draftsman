# test_curved_rail_a.py

from draftsman.constants import Direction
from draftsman.prototypes.curved_rail_a import (
    CurvedRailA,
    curved_rails_a,
)
from draftsman.warning import UnknownEntityWarning

import pytest


@pytest.fixture
def valid_curved_rail_a():
    if len(curved_rails_a) == 0:
        return None
    return CurvedRailA(
        "curved-rail-a",
        id="test",
        quality="uncommon",
        tile_position=(2, 2),
        direction=Direction.EAST,
        tags={"blah": "blah"},
    )


def test_constructor():
    curved_rail = CurvedRailA("curved-rail-a")

    with pytest.warns(UnknownEntityWarning):
        CurvedRailA("unknown curved rail")


def test_flags():
    for rail_name in curved_rails_a:
        curved_rail = CurvedRailA(rail_name)
        assert curved_rail.power_connectable == False
        assert curved_rail.dual_power_connectable == False
        assert curved_rail.circuit_connectable == False
        assert curved_rail.dual_circuit_connectable == False
