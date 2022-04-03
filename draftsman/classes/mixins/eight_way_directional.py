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
    Enables entities to be rotated across 8 directions.
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
        TODO
        """
        return self._direction

    @direction.setter
    def direction(self, value):
        # type: (Direction) -> None
        if self.blueprint:
            raise DraftsmanError(
                "Cannot set direction of entity while it's in a Blueprint"
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
