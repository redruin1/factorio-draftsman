# straight_rail.py

from draftsman.classes.collision_set import CollisionSet
from draftsman.classes.entity import Entity
from draftsman.classes.mixins import DoubleGridAlignedMixin, EightWayDirectionalMixin
from draftsman.classes.vector import Vector, PrimitiveVector
from draftsman.constants import Direction, ValidationMode
from draftsman.utils import AABB, Rectangle, get_first

from draftsman.data.entities import straight_rails

from pydantic import ConfigDict
from typing import Any, Literal, Optional, Union

# TODO: currently hardcoded just for straight rail
eps = 0.001
_vertical_collision = CollisionSet([AABB(-0.75, -1.0 + eps, 0.75, 1.0 - eps)])
_horizontal_collision = _vertical_collision.rotate(2)
_diagonal_collision = CollisionSet([Rectangle((-0.5, -0.5), 1.25, 1.40, 45)])
_collision_set_rotation = {}
_collision_set_rotation[Direction.NORTH] = _vertical_collision
_collision_set_rotation[Direction.NORTHEAST] = _diagonal_collision.rotate(2)
_collision_set_rotation[Direction.EAST] = _horizontal_collision
_collision_set_rotation[Direction.SOUTHEAST] = _diagonal_collision.rotate(4)
_collision_set_rotation[Direction.SOUTH] = _vertical_collision
_collision_set_rotation[Direction.SOUTHWEST] = _diagonal_collision.rotate(-2)
_collision_set_rotation[Direction.WEST] = _horizontal_collision
_collision_set_rotation[Direction.NORTHWEST] = _diagonal_collision

eps = 0.001
_vertical_collision = CollisionSet([AABB(-0.75, -1.0 + eps, 0.75, 1.0 - eps)])
_horizontal_collision = _vertical_collision.rotate(2)
_diagonal_collision = CollisionSet([Rectangle((-0.5, -0.5), 1.25, 1.40, 45)])
_collision_set_rotation = {}
_collision_set_rotation[Direction.NORTH] = _vertical_collision
_collision_set_rotation[Direction.NORTHEAST] = _diagonal_collision.rotate(2)
_collision_set_rotation[Direction.EAST] = _horizontal_collision
_collision_set_rotation[Direction.SOUTHEAST] = _diagonal_collision.rotate(4)
_collision_set_rotation[Direction.SOUTH] = _vertical_collision
_collision_set_rotation[Direction.SOUTHWEST] = _diagonal_collision.rotate(-2)
_collision_set_rotation[Direction.WEST] = _horizontal_collision
_collision_set_rotation[Direction.NORTHWEST] = _diagonal_collision


class StraightRail(DoubleGridAlignedMixin, EightWayDirectionalMixin, Entity):
    """
    An old, 1.0 straight rail entity.
    """

    class Format(
        DoubleGridAlignedMixin.Format, EightWayDirectionalMixin.Format, Entity.Format
    ):
        model_config = ConfigDict(title="StraightRail")

    def __init__(
        self,
        name: Optional[str] = get_first(straight_rails),
        position: Union[Vector, PrimitiveVector] = None,
        tile_position: Union[Vector, PrimitiveVector] = (0, 0),
        direction: Direction = Direction.NORTH,
        tags: dict[str, Any] = {},
        validate_assignment: Union[
            ValidationMode, Literal["none", "minimum", "strict", "pedantic"]
        ] = ValidationMode.STRICT,
        **kwargs
    ):
        """
        TODO
        """

        # This is kinda hacky, but necessary due to Factorio issuing dummy
        # values for collision boxes. We have to do this before initialization
        # of the rest of the class because certain things like tile position are
        # dependent on this information and can be set during initialization
        # (if we pass in arguments in **kwargs).

        # We set a (private) flag to ignore the dummy collision box that
        # Factorio provides
        self._overwritten_collision_set = True

        # We then provide a list of all the custom rotations
        self._collision_set = _vertical_collision
        self._collision_set_rotation = _collision_set_rotation

        super().__init__(
            name,
            straight_rails,
            position=position,
            tile_position=tile_position,
            direction=direction,
            tags=tags,
            **kwargs
        )

        self.validate_assignment = validate_assignment

    # =========================================================================

    @property
    def double_grid_aligned(self) -> bool:
        return True

    # =========================================================================

    @property
    def collision_set(self) -> Optional[CollisionSet]:
        return _collision_set_rotation.get(self.direction, None)

    # =========================================================================

    __hash__ = Entity.__hash__
