# legacy_curved_rail.py

# TODO: the width of the curved rail is calculated to be 5 when it's probably
# actually 4 internally; thus we should manually overwrite it here... somehow

from draftsman.classes.collision_set import CollisionSet
from draftsman.classes.entity import Entity
from draftsman.classes.mixins import DoubleGridAlignedMixin, DirectionalMixin
from draftsman.classes.mixins.directional import _rotated_collision_sets
from draftsman.classes.vector import Vector, PrimitiveVector
from draftsman.constants import Direction, ValidationMode, EIGHT_WAY_DIRECTIONS
from draftsman.utils import AABB, Rectangle, fix_incorrect_pre_init

from draftsman.data.entities import legacy_curved_rails

import attrs
from pydantic import ConfigDict
from typing import Any, Literal, Optional, Union

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
    Direction.NORTHWEST: _right_turn.rotate(12)
}


@fix_incorrect_pre_init
@attrs.define
class LegacyCurvedRail(DoubleGridAlignedMixin, DirectionalMixin, Entity):
    """
    An old, 1.0 curved rail entity.
    """

    # class Format(
    #     DoubleGridAlignedMixin.Format, EightWayDirectionalMixin.Format, Entity.Format
    # ):
    #     model_config = ConfigDict(title="LegacyCurvedRail")

    # def __init__(
    #     self,
    #     name: Optional[str] = get_first(legacy_curved_rails),
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

    #     # This is kinda hacky, but necessary due to Factorio issuing dummy
    #     # values for collision boxes. We have to do this before initialization
    #     # of the rest of the class because certain things like tile position are
    #     # dependent on this information and can be set during initialization
    #     # (if we pass in keyword arguments).

    #     # We set a (private) flag to ignore the dummy collision box that
    #     # Factorio provides
    #     self._overwritten_collision_set = True

    #     super().__init__(
    #         name,
    #         legacy_curved_rails,
    #         position=position,
    #         tile_position=tile_position,
    #         direction=direction,
    #         tags=tags,
    #         **kwargs
    #     )

    #     self.validate_assignment = validate_assignment

    # =========================================================================

    @property
    def similar_entities(self) -> list[str]:
        return legacy_curved_rails

    # =========================================================================

    @property
    def valid_directions(self) -> set[Direction]:
        return EIGHT_WAY_DIRECTIONS

    # =========================================================================

    __hash__ = Entity.__hash__
