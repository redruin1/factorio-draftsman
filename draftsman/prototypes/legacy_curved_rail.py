# legacy_curved_rail.py

from draftsman import DEFAULT_FACTORIO_VERSION
from draftsman.classes.collision_set import CollisionSet
from draftsman.classes.entity import Entity
from draftsman.classes.mixins import DirectionalMixin
from draftsman.classes.mixins.directional import _rotated_collision_sets
from draftsman.constants import Direction, EIGHT_WAY_DIRECTIONS
from draftsman.data import mods
from draftsman.utils import AABB, Rectangle

from draftsman.data.entities import legacy_curved_rails

import attrs

# Manually specified collision sets
_left_turn = CollisionSet(
    [AABB(0.25, 1.8, 1.75, 3.9), Rectangle((-0.375, -0.7175), 1.4, 5.45, -35)]
)
_right_turn = CollisionSet(
    [AABB(-1.75, 1.8, -0.25, 3.9), Rectangle((0.375, -0.7175), 1.4, 5.45, 35)]
)

# TODO: this doesn't update if the environment updates after loading this file...
# Also, this just kinda sucks
if mods.versions.get("base", DEFAULT_FACTORIO_VERSION) < (2, 0):
    _legacy_curved_rail_name = "curved-rail"
else:
    _legacy_curved_rail_name = "legacy-curved-rail"

_rotated_collision_sets[_legacy_curved_rail_name] = {
    Direction.NORTH: _left_turn,
    Direction.NORTHEAST: _right_turn,
    Direction.EAST: _left_turn.rotate(4),
    Direction.SOUTHEAST: _right_turn.rotate(4),
    Direction.SOUTH: _left_turn.rotate(8),
    Direction.SOUTHWEST: _right_turn.rotate(8),
    Direction.WEST: _left_turn.rotate(12),
    Direction.NORTHWEST: _right_turn.rotate(12),
}


@attrs.define
class LegacyCurvedRail(DirectionalMixin, Entity):
    """
    An old, Factorio 1.0 curved rail entity.
    """

    @property
    def similar_entities(self) -> list[str]:
        return legacy_curved_rails

    # =========================================================================

    @property
    def double_grid_aligned(self) -> bool:
        return True

    # =========================================================================

    @property
    def valid_directions(self) -> set[Direction]:
        return EIGHT_WAY_DIRECTIONS

    # =========================================================================

    @property
    def static_tile_width(self) -> int:
        return 4

    # =========================================================================

    @property
    def static_tile_height(self) -> int:
        return 8

    # =========================================================================

    @property
    def tile_width(self) -> int:
        if self.direction in {
            Direction.NORTH,
            Direction.NORTHEAST,
            Direction.SOUTH,
            Direction.SOUTHEAST,
        }:
            return 4
        else:
            return 8

    # =========================================================================

    @property
    def tile_height(self) -> int:
        if self.direction in {
            Direction.NORTH,
            Direction.NORTHEAST,
            Direction.SOUTH,
            Direction.SOUTHEAST,
        }:
            return 8
        else:
            return 4

    # =========================================================================

    __hash__ = Entity.__hash__
