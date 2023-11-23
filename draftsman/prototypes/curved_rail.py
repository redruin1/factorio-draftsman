# curved_rail.py

# TODO: the width of the curved rail is calculated to be 5 when it's probably
# actually 4 internally; thus we should manually overwrite it here... somehow

from draftsman.classes.collision_set import CollisionSet
from draftsman.classes.entity import Entity
from draftsman.classes.mixins import DoubleGridAlignedMixin, EightWayDirectionalMixin
from draftsman.classes.vector import Vector, PrimitiveVector
from draftsman.constants import Direction, ValidationMode
from draftsman.utils import AABB, Rectangle

from draftsman.data.entities import curved_rails

from pydantic import ConfigDict
from typing import Any, Literal, Optional, Union

_left_turn = CollisionSet(
    [AABB(0.25, 1.8, 1.75, 3.9), Rectangle((-0.375, -0.7175), 1.4, 5.45, -35)]
)
_right_turn = CollisionSet(
    [AABB(-1.75, 1.8, -0.25, 3.9), Rectangle((0.375, -0.7175), 1.4, 5.45, 35)]
)
_collision_set_rotation = {}
_collision_set_rotation[Direction.NORTH] = _left_turn
_collision_set_rotation[Direction.NORTHEAST] = _right_turn
_collision_set_rotation[Direction.EAST] = _left_turn.rotate(2)
_collision_set_rotation[Direction.SOUTHEAST] = _right_turn.rotate(2)
_collision_set_rotation[Direction.SOUTH] = _left_turn.rotate(4)
_collision_set_rotation[Direction.SOUTHWEST] = _right_turn.rotate(4)
_collision_set_rotation[Direction.WEST] = _left_turn.rotate(6)
_collision_set_rotation[Direction.NORTHWEST] = _right_turn.rotate(6)

_left_turn = CollisionSet(
    [AABB(0.25, 1.8, 1.75, 3.9), Rectangle((-0.375, -0.7175), 1.4, 5.45, -35)]
)
_right_turn = CollisionSet(
    [AABB(-1.75, 1.8, -0.25, 3.9), Rectangle((0.375, -0.7175), 1.4, 5.45, 35)]
)
_collision_set_rotation = {}
_collision_set_rotation[Direction.NORTH] = _left_turn
_collision_set_rotation[Direction.NORTHEAST] = _right_turn
_collision_set_rotation[Direction.EAST] = _left_turn.rotate(2)
_collision_set_rotation[Direction.SOUTHEAST] = _right_turn.rotate(2)
_collision_set_rotation[Direction.SOUTH] = _left_turn.rotate(4)
_collision_set_rotation[Direction.SOUTHWEST] = _right_turn.rotate(4)
_collision_set_rotation[Direction.WEST] = _left_turn.rotate(6)
_collision_set_rotation[Direction.NORTHWEST] = _right_turn.rotate(6)


class CurvedRail(DoubleGridAlignedMixin, EightWayDirectionalMixin, Entity):
    """
    A curved rail entity.
    """

    class Format(
        DoubleGridAlignedMixin.Format, EightWayDirectionalMixin.Format, Entity.Format
    ):
        model_config = ConfigDict(title="CurvedRail")

    def __init__(
        self,
        name: str = curved_rails[0],
        position: Union[Vector, PrimitiveVector] = None,
        tile_position: Union[Vector, PrimitiveVector] = (0, 0),
        direction: Direction = Direction.NORTH,
        tags: dict[str, Any] = {},
        validate: Union[
            ValidationMode, Literal["none", "minimum", "strict", "pedantic"]
        ] = ValidationMode.STRICT,
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
        # (if we pass in keyword arguments).

        # We set a (private) flag to ignore the dummy collision box that
        # Factorio provides
        self._overwritten_collision_set = True

        super().__init__(
            name,
            curved_rails,
            position=position,
            tile_position=tile_position,
            direction=direction,
            tags=tags,
            **kwargs
        )

        self.validate_assignment = validate_assignment

        self.validate(mode=validate).reissue_all(stacklevel=3)

    # =========================================================================

    @property
    def double_grid_aligned(self) -> bool:
        return True

    # =========================================================================

    @property
    def static_collision_set(self) -> Optional[CollisionSet]:
        return _collision_set_rotation.get(Direction.NORTH, None)

    # =========================================================================

    @property
    def collision_set(self) -> Optional[CollisionSet]:
        return _collision_set_rotation.get(self.direction, None)

    # =========================================================================

    __hash__ = Entity.__hash__
