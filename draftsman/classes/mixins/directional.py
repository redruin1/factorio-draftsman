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


class DirectionalMixin(object):
    """
    Allows the Entity to be rotated in the 4 cardinal directions. Sets the
    ``rotatable`` attribute to ``True``.

    .. seealso::

        :py:class:`~.mixins.eight_way_directional.EightWayDirectionalMixin`
    """

    def __init__(self, name, similar_entities, tile_position=[0, 0], **kwargs):
        # type: (str, list[str], Union[list, dict], **dict) -> None
        super(DirectionalMixin, self).__init__(name, similar_entities, **kwargs)

        self._rotatable = True

        # Keep track of the entities width and height regardless of rotation
        self._static_tile_width = self.tile_width
        self._static_tile_height = self.tile_height
        self._static_collision_set = self.collision_set

        # Technically this check is not necessary, but we include it for
        # completeness
        if not hasattr(self, "_overwritten_collision_set"):  # pragma: no branch
            self._collision_set_rotation = {}
            # if hasattr(self, "_disable_collision_set_rotation"):
            #     # Set every collision orientation to the single collision_set
            #     for i in {0, 2, 4, 6}:
            #         self._collision_set_rotation[i] = self.collision_set
            # else:
            # Automatically generate a set of rotated collision sets for every
            # orientation
            for i in {0, 2, 4, 6}:
                self._collision_set_rotation[i] = self._collision_set.rotate(i)

        self.direction = 0
        if "direction" in kwargs:
            self.direction = kwargs["direction"]
            self.unused_args.pop("direction")
        self._add_export("direction", lambda x: x != 0, lambda k, v: (k, int(v)))

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
        diagonal direction. For 8-way rotations, ensure that the Entity inherits
        :py:class:`.EightwayDirectionalMixin`.

        :getter: Gets the direction that the Entity is facing.
        :setter: Sets the direction of the Entity. Defaults to ``Direction.NORTH``
            if set to ``None``.
        :type: :py:data:`~draftsman.constants.Direction`

        :exception DraftsmanError: If the direction is set while inside an
            Collection, :ref:`which is forbidden
            <handbook.blueprints.forbidden_entity_attributes>`.
        :exception ValueError: If set to anything other than a ``Direction``, or
            its equivalent ``int``.
        """
        return self._direction

    @direction.setter
    def direction(self, value):
        # type: (Direction) -> None
        if self.parent:
            raise DraftsmanError(
                "Cannot set direction of entity while it's in another object"
            )

        if value is None:
            self._direction = Direction(0)  # Default Direction
        else:
            self._direction = Direction(value)

        if self._direction not in {0, 2, 4, 6}:
            warnings.warn(
                "'{}' only has 4-way rotation".format(type(self).__name__),
                DirectionWarning,
                stacklevel=2,
            )
            return

        # if self._direction == Direction.EAST or self._direction == Direction.WEST:
        #     self._tile_width = self.static_tile_height
        #     self._tile_height = self.static_tile_width
        #     self._collision_set = self.static_collision_set.rotate(self._direction)
        # else:
        #     self._tile_width = self.static_tile_width
        #     self._tile_height = self.static_tile_height
        #     self._collision_set = self.static_collision_set

        # Get the precalulated orientations
        self._collision_set = self._collision_set_rotation[self._direction]
        # TODO: do this better
        if self._direction == Direction.EAST or self._direction == Direction.WEST:
            self._tile_width = self._static_tile_height
            self._tile_height = self._static_tile_width
        else:
            self._tile_width = self._static_tile_width
            self._tile_height = self._static_tile_height
        # bounding_box = self._collision_set.get_bounding_box()
        # self._tile_width, self._tile_height = utils.aabb_to_dimensions(bounding_box)

        # Reset the grid/absolute positions in case the direction changed
        self.tile_position = (self.tile_position.x, self.tile_position.y)

    # =========================================================================

    def mergable_with(self, other):
        # type: (Entity) -> bool
        base_mergable = super(DirectionalMixin, self).mergable_with(other)
        return base_mergable and self.direction == other.direction
