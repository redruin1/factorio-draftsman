# legacy_curved_rail.py

# TODO: the width of the curved rail is calculated to be 5 when it's probably
# actually 4 internally; thus we should manually overwrite it here... somehow

from draftsman.classes.collision_set import CollisionSet
from draftsman.classes.entity import Entity
from draftsman.classes.mixins import DoubleGridAlignedMixin, DirectionalMixin
from draftsman.classes.mixins.directional import _rotated_collision_sets
from draftsman.constants import Direction, EIGHT_WAY_DIRECTIONS
from draftsman.utils import AABB, Rectangle, fix_incorrect_pre_init

from draftsman.data.entities import legacy_curved_rails

import attrs

# Manually specified collision sets
_left_turn = CollisionSet(
    [AABB(0.25, 1.8, 1.75, 3.9), Rectangle((-0.375, -0.7175), 1.4, 5.45, -35)]
)
_right_turn = CollisionSet(
    [AABB(-1.75, 1.8, -0.25, 3.9), Rectangle((0.375, -0.7175), 1.4, 5.45, 35)]
)
_rotated_collision_sets["legacy-curved-rail"] = {
    Direction.NORTH: _left_turn,
    Direction.NORTHEAST: _right_turn,
    Direction.EAST: _left_turn.rotate(4),
    Direction.SOUTHEAST: _right_turn.rotate(4),
    Direction.SOUTH: _left_turn.rotate(8),
    Direction.SOUTHWEST: _right_turn.rotate(8),
    Direction.WEST: _left_turn.rotate(12),
    Direction.NORTHWEST: _right_turn.rotate(12),
}


@fix_incorrect_pre_init
@attrs.define
class LegacyCurvedRail(DoubleGridAlignedMixin, DirectionalMixin, Entity):
    """
    An old, Factorio 1.0 curved rail entity.
    """

    @property
    def similar_entities(self) -> list[str]:
        return legacy_curved_rails

    # =========================================================================

    @property
    def valid_directions(self) -> set[Direction]:
        return EIGHT_WAY_DIRECTIONS

    # =========================================================================

    __hash__ = Entity.__hash__
