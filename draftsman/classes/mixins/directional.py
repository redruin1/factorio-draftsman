# directional.py

from draftsman import signatures
from draftsman.constants import Direction
from draftsman.warning import DirectionWarning

from schema import SchemaError
from typing import Union
import warnings


class DirectionalMixin(object):
    """ 
    Enables entities to be rotated. 
    """
    def __init__(self, name, similar_entities, position = [0, 0], **kwargs):
        # type: (str, list[str], Union[list, dict], **dict) -> None
        super(DirectionalMixin, self).__init__(name, similar_entities, **kwargs)

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
        self.position = position

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
        if value is None:
            value = 0 # Default Direction

        try:
            self._direction = signatures.DIRECTION.validate(value)
        except SchemaError:
            # TODO: more verbose
            raise TypeError("Invalid direction format")
        
        if self._direction not in {0, 2, 4, 6}:
            warnings.warn(
                "'{}' only has 4-way rotation".format(type(self).__name__),
                DirectionWarning,
                stacklevel = 2
            )
        if self._direction == Direction.EAST or self._direction == Direction.WEST:
            self._tile_width = self.static_tile_height
            self._tile_height = self.static_tile_width
            self._collision_box[0] = [self.static_collision_box[0][1],
                                      self.static_collision_box[0][0]]
            self._collision_box[1] = [self.static_collision_box[1][1],
                                      self.static_collision_box[1][0]]
        else:
            self._tile_width = self.static_tile_width
            self._tile_height = self.static_tile_height
            self._collision_box = self.static_collision_box
        
        # Reset the grid/absolute positions in case the direction changed
        self.set_tile_position(self.tile_position[0], self.tile_position[1])