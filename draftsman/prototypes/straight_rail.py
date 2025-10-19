# straight_rail.py

from draftsman.classes.collision_set import CollisionSet
from draftsman.classes.entity import Entity
from draftsman.classes.mixins import DirectionalMixin
from draftsman.constants import Direction, EIGHT_WAY_DIRECTIONS
from draftsman.utils import AABB, Rectangle

from draftsman.data.entities import straight_rails

import attrs


@attrs.define
class StraightRail(DirectionalMixin, Entity):
    """
    A piece of rail track that moves in the 8 cardinal directions.
    """

    @property
    def similar_entities(self) -> list[str]:
        return straight_rails

    # =========================================================================

    @property
    def double_grid_aligned(self) -> bool:
        return True

    # =========================================================================

    @property
    def tile_width(self) -> int:
        return 2

    # =========================================================================

    @property
    def tile_height(self) -> int:
        return 2

    # =========================================================================

    @property
    def valid_directions(self) -> set[Direction]:
        return EIGHT_WAY_DIRECTIONS

    # =========================================================================

    def _specify_collision_sets(self) -> dict:
        vertical = CollisionSet([AABB(-0.75, -0.99, 0.75, 0.99)])
        horizontal = vertical.rotate(4)
        diagonal = CollisionSet([Rectangle((0, 0), 1.5, 3.00, -45)])

        return {
            Direction.NORTH: vertical,
            Direction.NORTHEAST: diagonal.rotate(4),
            Direction.EAST: horizontal,
            Direction.SOUTHEAST: diagonal.rotate(8),
            Direction.SOUTH: vertical,
            Direction.SOUTHWEST: diagonal.rotate(-4),
            Direction.WEST: horizontal,
            Direction.NORTHWEST: diagonal,
        }

    __hash__ = Entity.__hash__
