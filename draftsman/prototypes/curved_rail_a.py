# curved_rail_a.py

from draftsman.classes.collision_set import CollisionSet
from draftsman.classes.entity import Entity
from draftsman.classes.mixins import DirectionalMixin
from draftsman.classes.mixins.directional import _rotated_collision_sets
from draftsman.constants import Direction, EIGHT_WAY_DIRECTIONS
from draftsman.utils import Rectangle

from draftsman.data.entities import curved_rails_a

import attrs

import math


@attrs.define
class CurvedRailA(DirectionalMixin, Entity):
    """
    Curved rails which connect straight rails to half-diagonal rails.
    """

    @property
    def similar_entities(self) -> list[str]:
        return curved_rails_a

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
        def q_x(d):
            return (
                -0.0001006957601695
                + d * 0.0006303089061514
                + d**2 * -0.0390775228531406
                + d**3 * 0.0001929289349940
            )

        def q_y(d):
            return (
                2.0000180760089301
                + d * -1.0001059650840689
                + d**2 * 0.0000918676400977
                + d**3 * 0.0009646884174780
            )

        # RailLength provided via boskid
        RailLength = 5.132284556
        Radius = 13.0
        angle = (RailLength / 2.0) / Radius

        # These are probably not exactly right, but they seem close enough for now
        xoff = 0.35
        yoff = 1.25
        left_curve = CollisionSet(
            [
                Rectangle(
                    (q_x(angle) - xoff, -q_y(angle) + yoff),
                    1.5,
                    5,
                    -math.degrees(angle),
                )
            ]
        )
        right_curve = CollisionSet(
            [
                Rectangle(
                    (-q_x(angle) + xoff, -q_y(angle) + yoff),
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
