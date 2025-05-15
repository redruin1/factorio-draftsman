# legacy_straight_rail.py

from draftsman.classes.collision_set import CollisionSet
from draftsman.classes.entity import Entity
from draftsman.classes.mixins import DoubleGridAlignedMixin, DirectionalMixin
from draftsman.classes.mixins.directional import _rotated_collision_sets
from draftsman.constants import Direction, EIGHT_WAY_DIRECTIONS
from draftsman.utils import AABB, Rectangle, fix_incorrect_pre_init

from draftsman.data.entities import legacy_straight_rails

import attrs


# Manually specified collision sets
eps = 0.001
_vertical_collision = CollisionSet([AABB(-0.75, -1.0 + eps, 0.75, 1.0 - eps)])
_horizontal_collision = _vertical_collision.rotate(4)
_diagonal_collision = CollisionSet([Rectangle((-0.5, -0.5), 1.25, 1.40, 45)])

_rotated_collision_sets["legacy-straight-rail"] = {
    Direction.NORTH: _vertical_collision,
    Direction.NORTHEAST: _diagonal_collision.rotate(4),
    Direction.EAST: _horizontal_collision,
    Direction.SOUTHEAST: _diagonal_collision.rotate(8),
    Direction.SOUTH: _vertical_collision,
    Direction.SOUTHWEST: _diagonal_collision.rotate(-4),
    Direction.WEST: _horizontal_collision,
    Direction.NORTHWEST: _diagonal_collision,
}


@fix_incorrect_pre_init
@attrs.define
class LegacyStraightRail(DoubleGridAlignedMixin, DirectionalMixin, Entity):
    """
    An old, Factorio 1.0 straight rail entity.
    """

    # =========================================================================

    @property
    def similar_entities(self) -> list[str]:
        return legacy_straight_rails

    # =========================================================================

    @property
    def valid_directions(self) -> set[Direction]:
        return EIGHT_WAY_DIRECTIONS

    # =========================================================================

    __hash__ = Entity.__hash__


LegacyStraightRail.add_schema({"$id": "urn:factorio:entity:legacy-straight-rail"})
