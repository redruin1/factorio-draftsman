# eight_way_directional.py
# -*- encoding: utf-8 -*-

from __future__ import unicode_literals

from draftsman import signatures
from draftsman.constants import Direction
from draftsman.error import DraftsmanError

from schema import SchemaError
from typing import Union


class EightWayDirectionalMixin(object):
    """
    Allows the Entity to be rotated in the 8 cardinal directions and diagonals.
    Sets the ``rotatable`` attribute to ``True``.

    .. seealso::

        :py:class:`~.mixins.directional.DirectionalMixin`
    """

    def __init__(self, name, similar_entities, tile_position=[0, 0], **kwargs):
        # type: (str, list[str], Union[list, dict], **dict) -> None
        super(EightWayDirectionalMixin, self).__init__(name, similar_entities, **kwargs)

        self._rotatable = True

        # Keep track of the entities width and height regardless of rotation
        self.static_tile_width = self.tile_width
        self.static_tile_height = self.tile_height
        self.static_collision_box = self.collision_box

        self.direction = 0
        if "direction" in kwargs:
            self.direction = kwargs["direction"]
            self.unused_args.pop("direction")
        self._add_export("direction", lambda x: x != 0)

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

        Note that for rail entities, what "direction" means to them is not
        entirely intuitive, especially in the diagonal directions. Proceed with
        caution.

        :getter: Gets the direction that the Entity is facing.
        :setter: Sets the direction of the Entity. Defaults to ``Direction.NORTH``
            if set to ``None``.
        :type: :py:data:`~draftsman.constants.Direction`

        :exception DraftsmanError: If the direction is set while inside an
            Collection, :ref:`which is forbidden.
            <handbook.blueprints.forbidden_entity_attributes>`
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

        if self._direction in {2, 3, 6, 7}:
            self._tile_width = self.static_tile_height
            self._tile_height = self.static_tile_width
            self._collision_box[0] = [
                self.static_collision_box[0][1],
                self.static_collision_box[0][0],
            ]
            self._collision_box[1] = [
                self.static_collision_box[1][1],
                self.static_collision_box[1][0],
            ]
        else:
            self._tile_width = self.static_tile_width
            self._tile_height = self.static_tile_height
            self._collision_box = self.static_collision_box

        # Reset the grid/absolute positions in case the direction changed
        # self.set_tile_position(self.tile_position[0], self.tile_position[1])
        self.tile_position = (self.tile_position["x"], self.tile_position["y"])
