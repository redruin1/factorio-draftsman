# directional.py
# -*- encoding: utf-8 -*-

from __future__ import unicode_literals

# from draftsman.classes.vector import Vector
from draftsman.constants import Direction
from draftsman.error import DraftsmanError
from draftsman import utils
from draftsman.warning import DirectionWarning

from typing import Union
import warnings

from typing import TYPE_CHECKING

if TYPE_CHECKING:  # pragma: no coverage
    from draftsman.classes.entity import Entity

_rotated_collision_sets = {}


class DirectionalMixin(object):
    """
    Allows the Entity to be rotated in the 4 cardinal directions. Sets the
    ``rotatable`` attribute to ``True``.

    .. seealso::

        :py:class:`~.mixins.eight_way_directional.EightWayDirectionalMixin`
    """

    _exports = {
        "direction": {
            "format": "int",
            "description": "The direction this entity is facing",
            "required": lambda x: x != 0,
        }
    }

    def __init__(self, name, similar_entities, tile_position=[0, 0], **kwargs):
        # type: (str, list[str], Union[list, dict], **dict) -> None
        super(DirectionalMixin, self).__init__(name, similar_entities, **kwargs)

        self._rotatable = True
        self._square = self._tile_width == self._tile_height

        # Keep track of the entities width and height regardless of rotation
        self._static_tile_width = self._tile_width
        self._static_tile_height = self._tile_height
        self._static_collision_set = self.collision_set

        # Technically this check is not necessary, but we include it for
        # completeness
        if not hasattr(self, "_overwritten_collision_set"):  # pragma: no branch
            # if hasattr(self, "_disable_collision_set_rotation"):
            #     # Set every collision orientation to the single collision_set
            #     for i in {0, 2, 4, 6}:
            #         self._collision_set_rotation[i] = self.collision_set
            # else:
            # Automatically generate a set of rotated collision sets for every
            # orientation
            try:
                self._collision_set_rotation = _rotated_collision_sets[self.name]
            except KeyError:
                # Cache it so we only need one
                # TODO: would probably be better to do this in env.py, but how?
                _rotated_collision_sets[self.name] = {}
                for i in {0, 2, 4, 6}:
                    _rotated_collision_sets[self.name][i] = self.collision_set.rotate(i)
                self._collision_set_rotation = _rotated_collision_sets[self.name]

        self.direction = 0
        if "direction" in kwargs:
            self.direction = kwargs["direction"]
            self.unused_args.pop("direction")
        # self._add_export("direction", lambda x: x != 0, lambda k, v: (k, int(v)))

        # Technically redundant, but we reset the position if the direction has
        # changed to reflect its changes
        if "position" in kwargs:
            self.position = kwargs["position"]
        else:
            self.tile_position = tile_position

    # =========================================================================

    @property
    def direction(self):
        # type: () -> Direction
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
        :type: :py:data:`~draftsman.constants.Direction`

        :exception DraftsmanError: If the direction is set while inside a
            Collection, and the target entity is both non-square and the
            particular rotation would change it's apparent tile width and height.
            See, :ref:`here<handbook.blueprints.forbidden_entity_attributes>`
            for more info.
        :exception ValueError: If set to anything other than a ``Direction``, or
            an equivalent ``int``.
        """
        return self._direction

    @direction.setter
    def direction(self, value):
        # type: (Direction) -> None

        # Check if the rotation would change the entity's tile width or height
        if value == Direction.EAST or value == Direction.WEST:
            new_tile_width = self._static_tile_height
            new_tile_height = self._static_tile_width
        else:
            new_tile_width = self._static_tile_width
            new_tile_height = self._static_tile_height

        if (
            self.parent
            and not self._square
            and new_tile_width != self._tile_width
            and new_tile_height != self._tile_height
        ):
            raise DraftsmanError(
                "Cannot set this direction of non-square entity while it's in "
                "another object; might intersect neighbours"
            )

        if value is None:
            self._direction = Direction(0)  # Default Direction
        else:
            self._direction = Direction(value)

        if self._direction not in {0, 2, 4, 6}:
            # Default to a known orientation
            self._direction = Direction(int(self._direction / 2) * 2)
            warnings.warn(
                "'{}' only has 4-way rotation; defaulting to {}".format(
                    type(self).__name__, self._direction
                ),
                DirectionWarning,
                stacklevel=2,
            )

        # Get the precalulated orientations
        self._collision_set = self._collision_set_rotation[self._direction]

        # Actually update tile width and height
        old_tile_width = self._tile_width
        old_tile_height = self._tile_height
        self._tile_width = new_tile_width
        self._tile_height = new_tile_height

        # Reset the grid/absolute positions in case the width and height are now
        # different
        if (
            not self._square
            and old_tile_width != new_tile_width
            and old_tile_height != new_tile_height
        ):
            self.tile_position = (self.tile_position.x, self.tile_position.y)

    # =========================================================================

    def mergable_with(self, other):
        # type: (Entity) -> bool
        base_mergable = super(DirectionalMixin, self).mergable_with(other)
        return base_mergable and self.direction == other.direction
