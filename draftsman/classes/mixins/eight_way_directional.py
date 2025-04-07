# eight_way_directional.py

from draftsman.classes.exportable import attempt_and_reissue
from draftsman.constants import Direction
from draftsman.signatures import IntPosition, uint8

import attrs
from pydantic import (
    BaseModel,
    Field,
    PrivateAttr,
    ValidationInfo,
    ValidatorFunctionWrapHandler,
    field_serializer,
    field_validator,
)
from typing import Any, Optional

from typing import TYPE_CHECKING

if TYPE_CHECKING:  # pragma: no coverage
    from draftsman.classes.entity import Entity


_rotated_collision_sets = {}


@attrs.define(slots=False)
class EightWayDirectionalMixin:
    """
    Allows the Entity to be rotated in the 8 cardinal directions and diagonals.
    Sets the ``rotatable`` attribute to ``True``.

    .. seealso::

        :py:class:`~.mixins.directional.DirectionalMixin`
    """

    class Format(BaseModel):
        direction: Optional[Direction] = Field(
            Direction.NORTH,
            ge=0,
            lt=256,
            description="""
            The grid-aligned direction this entity is facing. Direction can only
            be one of 8 distinct directions (cardinal directions and diagonals),
            which differs from 'orientation' which is used for RollingStock.
            """,
        )

    # def __init__(
    #     self,
    #     name: str,
    #     similar_entities: list[str],
    #     tile_position: IntPosition = (0, 0),
    #     **kwargs
    # ):
    #     self._root: __class__.Format

    #     super().__init__(name, similar_entities, **kwargs)

    #     # If 'None' was passed to position, treat that as the same as omission
    #     # We do this because we want to be able to annotate `position` in each
    #     # entity's __init__ signature and indicate that it's optional
    #     if "position" in kwargs and kwargs["position"] is None:
    #         del kwargs["position"]

    #     # Keep track of the entities width and height regardless of rotation
    #     self._static_tile_width = self._tile_width
    #     self._static_tile_height = self._tile_height
    #     # self._static_collision_set = self.collision_set

    #     if not hasattr(self, "_overwritten_collision_set"):
    #         self._collision_set_rotation = {}
    #         if hasattr(self, "_disable_collision_set_rotation"):  # pragma: no branch
    #             # Set every collision orientation to the single collision_set
    #             # for i in range(8):
    #             #     self._collision_set_rotation[i] = self.collision_set
    #             try:
    #                 self._collision_set_rotation = _rotated_collision_sets[self.name]
    #             except KeyError:
    #                 # Cache it so we only need one
    #                 # TODO: would probably be better to do this in env.py, but how?
    #                 _rotated_collision_sets[self.name] = {}
    #                 for i in range(8):
    #                     _rotated_collision_sets[self.name][i] = self.collision_set

    #                 self._collision_set_rotation = _rotated_collision_sets[self.name]
    #         # else:
    #         #     # Automatically generate a set of rotated collision sets for every
    #         #     # orientation
    #         #     for i in range(8):
    #         #         self._collision_set_rotation[i] = self._collision_set.rotate(i)

    #     self.direction = kwargs.get("direction", Direction.NORTH)

    #     # Technically redundant, but we reset the position if the direction has
    #     # changed to reflect its changes
    #     if "position" in kwargs:
    #         self.position = kwargs["position"]
    #     else:
    #         self.tile_position = tile_position

    # =========================================================================

    @property
    def rotatable(self) -> bool:
        return True

    # =========================================================================

    @property
    def square(self) -> bool:
        """
        Whether or not the tile width of this entity matches it's tile height.
        Not exported; read only.
        """
        return self._tile_width == self._tile_height

    # =========================================================================

    direction: Direction = attrs.field(
        default=Direction.NORTH,
        converter=Direction,
        validator=attrs.validators.instance_of(Direction),
    )
    """
    The direction that the Entity is facing. An Entity's "front" is usually
    the direction of it's outputs, if it has any.

    .. NOTE::
        When manipulating rail entities, what "direction" means to them is not
        entirely intuitive, especially in the diagonal directions. Proceed with
        caution in this case.
    """

    # @property
    # def direction(self) -> Direction:
    #     """
    #     The direction that the Entity is facing. An Entity's "front" is usually
    #     the direction of it's outputs, if it has any.

    #     Note that for rail entities, what "direction" means to them is not
    #     entirely intuitive, especially in the diagonal directions. Proceed with
    #     caution.

    #     :getter: Gets the direction that the Entity is facing.
    #     :setter: Sets the direction of the Entity. Defaults to ``Direction.NORTH``
    #         if set to ``None``.

    #     :exception DraftsmanError: If the direction is set while inside an
    #         Collection, :ref:`which is forbidden.
    #         <handbook.blueprints.forbidden_entity_attributes>`
    #     :exception ValueError: If set to anything other than a ``Direction``, or
    #         its equivalent ``int``.
    #     """
    #     return self._root.direction

    # @direction.setter
    # def direction(self, value: Direction):
    #     if self.validate_assignment:
    #         result = attempt_and_reissue(
    #             self, type(self).Format, self._root, "direction", value
    #         )
    #         self._root.direction = result
    #     else:
    #         self._root.direction = value

    #     # if self.parent:
    #     #     raise DraftsmanError(
    #     #         "Cannot set direction of entity while it's in another object"
    #     #     )

    #     # if value is None:
    #     #     self._root["direction"] = Direction(0)  # Default Direction
    #     # else:
    #     #     self._root["direction"] = Direction(value)

    #     # if self._root.direction in {2, 3, 6, 7}:
    #     #     self._tile_width = self._static_tile_height
    #     #     self._tile_height = self._static_tile_width
    #     # self._collision_box[0] = [
    #     #     self.static_collision_box[0][1],
    #     #     self.static_collision_box[0][0],
    #     # ]
    #     # self._collision_box[1] = [
    #     #     self.static_collision_box[1][1],
    #     #     self.static_collision_box[1][0],
    #     # ]
    #     # else:
    #     #     self._tile_width = self._static_tile_width
    #     #     self._tile_height = self._static_tile_height
    #     # self._collision_box = self.static_collision_box

    #     # self._collision_set = self._collision_set_rotation.get(
    #     #     self._root.direction, None
    #     # )

    #     # TODO: overwrite tile_width/height properties instead
    #     if self._root.direction in {2, 3, 6, 7}:
    #         self._tile_width = self._static_tile_height
    #         self._tile_height = self._static_tile_width
    #     else:
    #         self._tile_width = self._static_tile_width
    #         self._tile_height = self._static_tile_height

    #     # Reset the grid/absolute positions in case the direction changed
    #     # self.tile_position = (self.tile_position.x, self.tile_position.y)
    #     self.tile_position = self.tile_position

    # =========================================================================

    def mergable_with(self, other: "EightWayDirectionalMixin") -> bool:
        base_mergable = super().mergable_with(other)
        return base_mergable and self.direction == other.direction

    # =========================================================================

    # def __eq__(self, other) -> bool:
    #     return super().__eq__(other) and self.direction == other.direction
