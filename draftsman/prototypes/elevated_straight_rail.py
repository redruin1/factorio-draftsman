# elevated_straight_rail.py

from draftsman.classes.collision_set import CollisionSet
from draftsman.classes.entity import Entity
from draftsman.classes.mixins import DoubleGridAlignedMixin, DirectionalMixin
from draftsman.classes.mixins.directional import _rotated_collision_sets
from draftsman.classes.vector import Vector, PrimitiveVector
from draftsman.constants import Direction, ValidationMode, EIGHT_WAY_DIRECTIONS
from draftsman.utils import AABB, Rectangle, fix_incorrect_pre_init

from draftsman.data.entities import elevated_straight_rails

import attrs
from pydantic import ConfigDict
from typing import Any, Literal, Optional, Union


# Manually specified collision sets
_vertical_collision = CollisionSet([AABB(-0.75, -0.99, 0.75, 0.99)])
_horizontal_collision = _vertical_collision.rotate(4)
_diagonal_collision = CollisionSet([Rectangle((-0.5, -0.5), 1.25, 1.40, 45)])

for rail_name in elevated_straight_rails:
    _rotated_collision_sets[rail_name] = {
        Direction.NORTH: _vertical_collision,
        Direction.NORTHEAST: _diagonal_collision.rotate(4),
        Direction.EAST: _horizontal_collision,
        Direction.SOUTHEAST: _diagonal_collision.rotate(8),
        Direction.SOUTH: _vertical_collision,
        Direction.SOUTHWEST: _diagonal_collision.rotate(-4),
        Direction.WEST: _horizontal_collision,
        Direction.NORTHWEST: _diagonal_collision
    }

@fix_incorrect_pre_init
@attrs.define
class ElevatedStraightRail(DoubleGridAlignedMixin, DirectionalMixin, Entity):
    """
    Straight rail entities the lie on a layer above regular entities. (TODO)
    """

    # class Format(
    #     DoubleGridAlignedMixin.Format, EightWayDirectionalMixin.Format, Entity.Format
    # ):
    #     model_config = ConfigDict(title="ElevatedStraightRail")

    # def __init__(
    #     self,
    #     name: Optional[str] = get_first(elevated_straight_rails),
    #     position: Union[Vector, PrimitiveVector] = None,
    #     tile_position: Union[Vector, PrimitiveVector] = (0, 0),
    #     direction: Direction = Direction.NORTH,
    #     tags: dict[str, Any] = {},
    #     validate_assignment: Union[
    #         ValidationMode, Literal["none", "minimum", "strict", "pedantic"]
    #     ] = ValidationMode.STRICT,
    #     **kwargs
    # ):
    #     """
    #     TODO
    #     """

    #     super().__init__(
    #         name,
    #         elevated_straight_rails,
    #         position=position,
    #         tile_position=tile_position,
    #         direction=direction,
    #         tags=tags,
    #         **kwargs
    #     )

    #     self.validate_assignment = validate_assignment

    @property
    def similar_entities(self) -> list[str]:
        return elevated_straight_rails

    # =========================================================================

    @property
    def valid_directions(self) -> set[Direction]:
        return EIGHT_WAY_DIRECTIONS

    # =========================================================================

    __hash__ = Entity.__hash__
