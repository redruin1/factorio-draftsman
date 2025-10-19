# curved_rail_b.py

from draftsman.classes.collision_set import CollisionSet
from draftsman.classes.entity import Entity
from draftsman.classes.mixins import DirectionalMixin
from draftsman.constants import Direction, EIGHT_WAY_DIRECTIONS
from draftsman.utils import Rectangle

from draftsman.data.entities import curved_rails_b

import attrs

import math


@attrs.define
class CurvedRailB(DirectionalMixin, Entity):
    """
    Curved rails which connect half-diagonal rails to diagonal rails.
    """

    @property
    def similar_entities(self) -> list[str]:
        return curved_rails_b

    # =========================================================================

    @property
    def double_grid_aligned(self) -> bool:
        return True

    # =========================================================================

    @property
    def valid_directions(self) -> set[Direction]:
        return EIGHT_WAY_DIRECTIONS

    # =========================================================================

    def _specify_collision_sets(self) -> dict:
        # Spline tables defined here:
        # https://forums.factorio.com/viewtopic.php?p=595840#p595840
        def p_x(d):
            return (
                0.9999296427835839
                + d * -0.4336250111930321
                + d**2 * -0.0343689574670654
                + d**3 * 0.0006729125223222
            )

        def p_y(d):
            return (
                2.0000700817657306
                + d * -0.9029070058349963
                + d**2 * 0.0190210273499390
                + d**3 * 0.0007210510062280
            )

        # RailLength provided via boskid
        RailLength = 5.132284556
        Radius = 13.0
        angle = (RailLength + RailLength / 2.0) / Radius

        # These are probably not exactly right, but they seem close enough for now
        xoff = 1.0
        yoff = 1.5
        left_curve = CollisionSet(
            [
                Rectangle(
                    (p_x(angle) - xoff, -p_y(angle) + yoff),
                    1.5,
                    5,
                    -math.degrees(angle),
                )
            ]
        )
        right_curve = CollisionSet(
            [
                Rectangle(
                    (-p_x(angle) + xoff, -p_y(angle) + yoff),
                    1.5,
                    5,
                    math.degrees(angle),
                )
            ]
        )
        return {
            Direction.NORTH: left_curve,
            Direction.NORTHEAST: right_curve,
            Direction.EAST: left_curve.rotate(4),
            Direction.SOUTHEAST: right_curve.rotate(4),
            Direction.SOUTH: left_curve.rotate(8),
            Direction.SOUTHWEST: right_curve.rotate(8),
            Direction.WEST: left_curve.rotate(12),
            Direction.NORTHWEST: right_curve.rotate(12),
        }

    __hash__ = Entity.__hash__
