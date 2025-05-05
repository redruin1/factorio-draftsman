# test_constants.py

from draftsman.constants import Direction, LegacyDirection
from draftsman.utils import Vector


def test_opposite_direction():
    assert Direction.NORTH.opposite() is Direction.SOUTH

    assert LegacyDirection.NORTH.opposite() is LegacyDirection.SOUTH

def test_next_direction():
    assert Direction.NORTH.next() is Direction.EAST
    assert Direction.NORTH.next(eight_way=True) is Direction.NORTHEAST

    assert LegacyDirection.NORTH.next() is LegacyDirection.EAST
    assert LegacyDirection.NORTH.next(eight_way=True) is LegacyDirection.NORTHEAST

def test_previous_direction():
    assert Direction.NORTH.previous() is Direction.WEST
    assert Direction.NORTH.previous(eight_way=True) is Direction.NORTHWEST

    assert LegacyDirection.NORTH.previous() is LegacyDirection.WEST
    assert LegacyDirection.NORTH.previous(eight_way=True) is LegacyDirection.NORTHWEST

def test_direction_to_orientation():
    assert Direction.NORTH.to_orientation() == 0.0
    assert Direction.SOUTH.to_orientation() == 0.5

    assert LegacyDirection.NORTH.to_orientation() == 0.0
    assert LegacyDirection.SOUTH.to_orientation() == 0.5

def test_direction_to_vector():
    assert Direction.EAST.to_vector() == Vector(1, 0)
    assert LegacyDirection.EAST.to_vector() == Vector(1, 0)

def test_direction_conversion():
    assert Direction.NORTH.to_legacy() is LegacyDirection.NORTH

    assert LegacyDirection.SOUTH.to_modern() is Direction.SOUTH