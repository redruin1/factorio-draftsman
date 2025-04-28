# directional.py

from draftsman.classes.collision_set import CollisionSet
from draftsman.constants import Direction, ValidationMode
from draftsman.data import entities
from draftsman.serialization import draftsman_converters
from draftsman.validators import and_, enum_converter, instance_of
from draftsman.utils import aabb_to_dimensions, get_first
from draftsman.warning import DirectionWarning

import attrs
import functools
from pydantic import (
    BaseModel,
    Field,
    ValidationInfo,
    field_validator,
)
from typing import Any, Optional
import warnings

from typing import TYPE_CHECKING

if TYPE_CHECKING:  # pragma: no coverage
    from draftsman.classes.entity import Entity

_rotated_collision_sets: dict[str, list[CollisionSet]] = {}

# def replace_init(cls):
#     original_init = cls.__init__

#     def new_init(self, *args, **kwargs):
#         self.__attrs_pre_init__(*args, **kwargs)
#         original_init(*args, **kwargs)

#     return cls


@attrs.define(slots=False)
class DirectionalMixin:
    """
    Allows the Entity to be rotated in the 4 cardinal directions. Sets the
    ``rotatable`` attribute to ``True``.

    .. seealso::

        :py:class:`~.mixins.eight_way_directional.EightWayDirectionalMixin`
    """

    class Format(BaseModel):
        direction: Optional[Direction] = Field(
            Direction.NORTH,
            ge=0,
            lt=256,
            description="""
            The grid-aligned direction this entity is facing. Direction can only
            be one of 4 distinct (cardinal) directions, which differs from 
            'orientation' which is used for RollingStock.
            """,
        )

        @field_validator("direction")
        @classmethod
        def ensure_4_way(cls, input: Optional[Direction], info: ValidationInfo):
            if not info.context:
                return input
            if info.context["mode"] <= ValidationMode.MINIMUM:
                return input

            warning_list: list = info.context["warning_list"]
            entity: Entity = info.context["object"]

            if input not in {0, 4, 8, 12}:
                # Default to a known orientation
                output = Direction(int(input / 4) * 4)

                warning_list.append(
                    DirectionWarning(
                        "'{}' only has 4-way rotation; defaulting to {}".format(
                            type(entity).__name__, output
                        ),
                    )
                )

                return output
            else:
                return input

    def __attrs_pre_init__(self, name=attrs.NOTHING, first_call=None, **kwargs):
        # Make sure this is the first time calling pre-init (bugfix until attrs
        # is patched)
        if not first_call:
            return

        # Call parent pre-init
        super().__attrs_pre_init__()
        # name = kwargs.get("name", get_first(self.similar_entities))
        name = name if name is not attrs.NOTHING else get_first(self.similar_entities)
        # print(name)

        # We generate collision sets on an as-needed basis for each unique
        # entity that is instantiated
        # Automatically generate a set of rotated collision sets for every
        # orientation
        try:
            _rotated_collision_sets[name]
        except KeyError:
            # Automatically generate a set of rotated collision sets for every
            # orientation
            # TODO: would probably be better to do this in env.py, but how?
            known_collision_set = entities.collision_sets.get(name, None)
            if known_collision_set:
                _rotated_collision_sets[name] = {}
                for i in {
                    Direction.NORTH,
                    Direction.EAST,
                    Direction.SOUTH,
                    Direction.WEST,
                }:
                    _rotated_collision_sets[name][i] = known_collision_set.rotate(i)
            else:
                _rotated_collision_sets[name] = {}
                for i in {
                    Direction.NORTH,
                    Direction.EAST,
                    Direction.SOUTH,
                    Direction.WEST,
                }:
                    _rotated_collision_sets[name][i] = None

        # The default position function uses `tile_width`/`tile_height`, which
        # use `collision_set`, which for rotatable entities is derived from the
        # current `direction`. However, since direction is specified *after*
        # position sequentially (and there is no way to easily rearrange them
        # since they are inherited), we need to manually "patch" the given value
        # of direction before the rest of the attribute setting code has run.
        # We use `object.__setattr__()` to circumvent the fact that we gave
        # `direction` a custom setattr function and mimic a "raw" attribute set.
        direction = kwargs.get("direction", Direction.NORTH)
        object.__setattr__(self, "direction", direction)

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

    #     # Technically this check is not necessary, but we include it for
    #     # completeness
    #     if not hasattr(self, "_overwritten_collision_set"):  # pragma: no branch
    #         # Automatically generate a set of rotated collision sets for every
    #         # orientation
    #         try:
    #             _rotated_collision_sets[name]
    #         except KeyError:
    #             # Cache it so we only need one
    #             # TODO: would probably be better to do this in env.py, but how?
    #             if super().collision_set:
    #                 _rotated_collision_sets[name] = {}
    #                 for i in {
    #                     Direction.NORTH,
    #                     Direction.EAST,
    #                     Direction.SOUTH,
    #                     Direction.WEST,
    #                 }:
    #                     _rotated_collision_sets[name][i] = super().collision_set.rotate(
    #                         i
    #                     )
    #             else:
    #                 _rotated_collision_sets[name] = {}
    #                 for i in {
    #                     Direction.NORTH,
    #                     Direction.EAST,
    #                     Direction.SOUTH,
    #                     Direction.WEST,
    #                 }:
    #                     _rotated_collision_sets[name][i] = None
    #             # self._collision_set_rotation = _rotated_collision_sets[self.name]

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
        return self.tile_width == self.tile_height

    # =========================================================================

    @property
    def static_tile_width(self) -> int:
        """
        The width of the entity irrespective of it's current orientation.
        Equivalent to the :py:attr:`.tile_width` when the entity is facing north.
        """
        return super().tile_width

    # =========================================================================

    @property
    def static_tile_height(self) -> int:
        """
        The height of the entity irrespective of it's current orientation.
        Equivalent to the :py:attr:`.tile_width` when the entity is facing north.
        """
        return super().tile_height

    # =========================================================================

    @property
    def collision_set(self) -> Optional[CollisionSet]:
        try:
            return _rotated_collision_sets.get(self.name, {}).get(self.direction.to_4_way(), None)
        except AttributeError:
            return None

    # =========================================================================

    @property  # Cache?
    def tile_width(self) -> int:
        if "tile_width" in self.prototype and "tile_height" in self.prototype:
            if self.direction in {Direction.EAST, Direction.WEST}:
                return self.prototype["tile_height"]
            else:
                return self.prototype["tile_width"]
        else:
            return aabb_to_dimensions(
                self.collision_set.get_bounding_box() if self.collision_set else None
            )[0]

    # =========================================================================

    @property  # Cache?
    def tile_height(self) -> int:
        if "tile_width" in self.prototype and "tile_height" in self.prototype:
            if self.direction in {Direction.EAST, Direction.WEST}:
                return self.prototype["tile_width"]
            else:
                return self.prototype["tile_height"]
        else:
            return aabb_to_dimensions(
                self.collision_set.get_bounding_box() if self.collision_set else None
            )[1]

    # =========================================================================

    def _set_direction(self, attr: attrs.Attribute, value: Any):
        # self.direction = value
        value = attr.converter(value)
        attr.validator(self, attr, value, mode=self.validate_assignment)
        value: Direction
        object.__setattr__(self, "direction", value)  # Prevent recursion

        if not self.square:
            self.tile_position = self.tile_position

        return value

    def ensure_4_way_direction(
        self, _: attrs.Attribute, value: Any, mode: Optional[ValidationMode] = None
    ):
        mode = mode if mode is not None else self.validate_assignment
        if mode >= ValidationMode.STRICT:
            if value not in {
                Direction.NORTH,
                Direction.EAST,
                Direction.SOUTH,
                Direction.WEST,
            }:
                # TODO: should we convert it for the user, or let it be wrong?
                warnings.warn(
                    DirectionWarning(
                        "'{}' only has 4-way rotation; will be converted to the value '{}' on import".format(
                            type(self).__name__, Direction(int(value / 4) * 4)
                        ),
                    )
                )

    direction: Direction = attrs.field(
        default=Direction.NORTH,
        converter=enum_converter(Direction),
        validator=and_(instance_of(Direction), ensure_4_way_direction),
        on_setattr=_set_direction,
    )
    """
    The direction that the Entity is facing. An Entity's "front" is usually
    the direction of it's outputs, if it has any.

    For some entities, this attribute may be redundant; for example, the
    direction value for an :py:class:`.AssemblingMachine` only matters if
    the machine has a fluid input or output.

    Raises :py:class:`~draftsman.warning.DirectionWarning` if set to a
    diagonal direction. In that case, the direction will default to the
    closest valid direction going counter-clockwise.

    :exception DraftsmanError: If the direction is set while inside a
        Collection, and the target entity is both non-square and the
        particular rotation would change it's apparent tile width and height.
        See, :ref:`here<handbook.blueprints.forbidden_entity_attributes>`
        for more info.
    :exception ValueError: If set to anything other than a ``Direction``, or
        an equivalent ``int``.
    """

    # @property
    # def direction(self) -> Optional[Direction]:
    #     """
    #     The direction that the Entity is facing. An Entity's "front" is usually
    #     the direction of it's outputs, if it has any.

    #     For some entities, this attribute may be redundant; for example, the
    #     direction value for an :py:class:`.AssemblingMachine` only matters if
    #     the machine has a fluid input or output.

    #     Raises :py:class:`~draftsman.warning.DirectionWarning` if set to a
    #     diagonal direction. In that case, the direction will default to the
    #     closest valid direction going counter-clockwise. For 8-way rotations,
    #     ensure that the Entity inherits :py:class:`.EightwayDirectionalMixin`
    #     instead.

    #     :getter: Gets the direction that the Entity is facing.
    #     :setter: Sets the direction of the Entity. Defaults to ``Direction.NORTH``
    #         if set to ``None``.

    #     :exception DraftsmanError: If the direction is set while inside a
    #         Collection, and the target entity is both non-square and the
    #         particular rotation would change it's apparent tile width and height.
    #         See, :ref:`here<handbook.blueprints.forbidden_entity_attributes>`
    #         for more info.
    #     :exception ValueError: If set to anything other than a ``Direction``, or
    #         an equivalent ``int``.
    #     """
    #     return self._root.direction

    # @direction.setter
    # def direction(self, value: Optional[Direction]):
    #     if self.validate_assignment:
    #         result = attempt_and_reissue(
    #             self, type(self).Format, self._root, "direction", value
    #         )
    #         self._root.direction = result
    #     else:
    #         self._root.direction = value

    #     # Update the collision set
    #     # self._collision_set = self._collision_set_rotation.get(
    #     #     self._root.direction, None
    #     # )

    #     # Check if the rotation would change the entity's tile width or height
    #     if value == Direction.EAST or value == Direction.WEST:
    #         new_tile_width = self._static_tile_height
    #         new_tile_height = self._static_tile_width
    #     else:
    #         new_tile_width = self._static_tile_width
    #         new_tile_height = self._static_tile_height

    #     # Actually update tile width and height
    #     old_tile_width = self._tile_width
    #     old_tile_height = self._tile_height
    #     self._tile_width = new_tile_width
    #     self._tile_height = new_tile_height

    #     # Reset the grid/absolute positions in case the width and height are now
    #     # different
    #     if (
    #         not self.square
    #         and old_tile_width != new_tile_width
    #         and old_tile_height != new_tile_height
    #     ):
    #         self.tile_position = self.tile_position

    # =========================================================================

    def mergable_with(self, other: "Entity") -> bool:
        base_mergable = super().mergable_with(other)
        return base_mergable and self.direction == other.direction

    # =========================================================================

    # def __eq__(self, other) -> bool:
    #     return super().__eq__(other) and self.direction == other.direction


draftsman_converters.add_schema(
    {"$id": "factorio:directional_mixin"},
    DirectionalMixin,
    lambda fields: {"direction": fields.direction.name},
)
