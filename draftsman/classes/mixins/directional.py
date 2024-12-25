# directional.py

from draftsman.classes.collision_set import CollisionSet
from draftsman.classes.exportable import attempt_and_reissue
from draftsman.signatures import IntPosition
from draftsman.constants import Direction, ValidationMode
from draftsman.error import DraftsmanError
from draftsman.warning import DirectionWarning

from pydantic import (
    BaseModel,
    Field,
    ValidationInfo,
    field_validator,
)
from typing import Optional

from typing import TYPE_CHECKING

if TYPE_CHECKING:  # pragma: no coverage
    from draftsman.classes.entity import Entity

_rotated_collision_sets: dict[str, list[CollisionSet]] = {}


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

            if input not in {Direction.NORTH, Direction.EAST, Direction.SOUTH, Direction.WEST}:
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

    def __init__(
        self,
        name: str,
        similar_entities: list[str],
        tile_position: IntPosition = (0, 0),
        **kwargs
    ):
        self._root: __class__.Format

        super().__init__(name, similar_entities, **kwargs)

        # If 'None' was passed to position, treat that as the same as omission
        # We do this because we want to be able to annotate `position` in each
        # entity's __init__ signature and indicate that it's optional
        if "position" in kwargs and kwargs["position"] is None:
            del kwargs["position"]

        # Keep track of the entities width and height regardless of rotation
        self._static_tile_width = self._tile_width
        self._static_tile_height = self._tile_height
        # self._static_collision_set = self.collision_set

        # Technically this check is not necessary, but we include it for
        # completeness
        if not hasattr(self, "_overwritten_collision_set"):  # pragma: no branch
            # Automatically generate a set of rotated collision sets for every
            # orientation
            try:
                _rotated_collision_sets[name]
            except KeyError:
                # Cache it so we only need one
                # TODO: would probably be better to do this in env.py, but how?
                if super().collision_set:
                    _rotated_collision_sets[name] = {}
                    for i in {Direction.NORTH, Direction.EAST, Direction.SOUTH, Direction.WEST}:
                        _rotated_collision_sets[name][i] = super().collision_set.rotate(
                            i/2
                        )
                else:
                    _rotated_collision_sets[name] = {}
                    for i in {Direction.NORTH, Direction.EAST, Direction.SOUTH, Direction.WEST}:
                        _rotated_collision_sets[name][i] = None
                # self._collision_set_rotation = _rotated_collision_sets[self.name]

        self.direction = kwargs.get("direction", Direction.NORTH)

        # Technically redundant, but we reset the position if the direction has
        # changed to reflect its changes
        if "position" in kwargs:
            self.position = kwargs["position"]
        else:
            self.tile_position = tile_position

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

    @property
    def static_collision_set(self) -> Optional[CollisionSet]:
        # return _rotated_collision_sets.get(self.name, {}).get(Direction.NORTH, None)
        return super().collision_set

    # =========================================================================

    @property
    def collision_set(self) -> Optional[CollisionSet]:
        return _rotated_collision_sets.get(self.name, {}).get(self.direction, None)

    # =========================================================================

    @property
    def direction(self) -> Optional[Direction]:
        """
        The direction that the Entity is facing. An Entity's "front" is usually
        the direction of it's outputs, if it has any.

        For some entities, this attribute may be redundant; for example, the
        direction value for an :py:class:`.AssemblingMachine` only matters if
        the machine has a fluid input or output.

        Raises :py:class:`~draftsman.warning.DirectionWarning` if set to a
        diagonal direction. In that case, the direction will default to the
        closest valid direction going counter-clockwise. For 8-way rotations,
        ensure that the Entity inherits :py:class:`.EightwayDirectionalMixin`
        instead.

        :getter: Gets the direction that the Entity is facing.
        :setter: Sets the direction of the Entity. Defaults to ``Direction.NORTH``
            if set to ``None``.

        :exception DraftsmanError: If the direction is set while inside a
            Collection, and the target entity is both non-square and the
            particular rotation would change it's apparent tile width and height.
            See, :ref:`here<handbook.blueprints.forbidden_entity_attributes>`
            for more info.
        :exception ValueError: If set to anything other than a ``Direction``, or
            an equivalent ``int``.
        """
        return self._root.direction

    @direction.setter
    def direction(self, value: Optional[Direction]):
        if self.validate_assignment:
            result = attempt_and_reissue(
                self, type(self).Format, self._root, "direction", value
            )
            self._root.direction = result
        else:
            self._root.direction = value

        # Update the collision set
        # self._collision_set = self._collision_set_rotation.get(
        #     self._root.direction, None
        # )

        # Check if the rotation would change the entity's tile width or height
        if value == Direction.EAST or value == Direction.WEST:
            new_tile_width = self._static_tile_height
            new_tile_height = self._static_tile_width
        else:
            new_tile_width = self._static_tile_width
            new_tile_height = self._static_tile_height

        # Actually update tile width and height
        old_tile_width = self._tile_width
        old_tile_height = self._tile_height
        self._tile_width = new_tile_width
        self._tile_height = new_tile_height

        # Reset the grid/absolute positions in case the width and height are now
        # different
        if (
            not self.square
            and old_tile_width != new_tile_width
            and old_tile_height != new_tile_height
        ):
            self.tile_position = self.tile_position

    # =========================================================================

    def mergable_with(self, other: "Entity") -> bool:
        base_mergable = super().mergable_with(other)
        return base_mergable and self.direction == other.direction

    # =========================================================================

    def __eq__(self, other) -> bool:
        return super().__eq__(other) and self.direction == other.direction
