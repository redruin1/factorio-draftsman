# half_diagonal_rail.py

from draftsman.constants import Direction, EIGHT_WAY_DIRECTIONS
from draftsman.classes.entity import Entity
from draftsman.classes.mixins import DirectionalMixin
from draftsman.utils import AABB, Rectangle

from draftsman.data import entities
from draftsman.data.entities import half_diagonal_rails

import attrs

import math


@attrs.define
class HalfDiagonalRail(DirectionalMixin, Entity):
    """
    .. versionadded:: 3.0.0 (Factorio 2.0)

    Rail entities which lie halfway inbetween the classic 45 degree diagonals.
    """

    @property
    def similar_entities(self) -> list[str]:
        return half_diagonal_rails

    # =========================================================================

    @property
    def valid_directions(self) -> set[Direction]:
        return EIGHT_WAY_DIRECTIONS

    # =========================================================================

    def _specify_collision_sets(self):
        result = {}
        # Take the original AABB and convert it to a slightly canted Rectangle
        # Not quite right either, but close enough for now
        static_collision_set = entities.collision_sets.get(self.name, None)
        aabb: AABB = static_collision_set.shapes[0]
        width = aabb.bot_right.x - aabb.top_left.x
        height = 4.0  # (aabb.bot_right.y - aabb.top_left.y)
        angle = math.degrees(0.07379 * 2.0 * math.pi)
        static_collision_set.shapes[0] = Rectangle((0, 0), width, height, -angle)

        for dir in self.valid_directions:
            if self.collision_set_rotated and static_collision_set is not None:
                rotated_collision_set = static_collision_set.rotate(dir)
            else:
                rotated_collision_set = static_collision_set

            result[dir] = rotated_collision_set
        return result

    __hash__ = Entity.__hash__
