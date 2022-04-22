# double_grid_aligned.py
# -*- encoding: utf-8 -*-

from __future__ import unicode_literals

from draftsman.warning import RailAlignmentWarning

import math
from typing import Union
import warnings


class DoubleGridAlignedMixin(object):
    """ """

    def __init__(self, name, similar_entities, **kwargs):
        # type: (str, list[str], **dict) -> None
        super(DoubleGridAlignedMixin, self).__init__(name, similar_entities, **kwargs)

        self._double_grid_aligned = True

        # Technically redundant, but we do this to ensure any warnings are met
        # TODO: maybe remove? Analyze the heirarchy here
        if "position" in kwargs:
            self.position = kwargs["position"]
        elif "tile_position" in kwargs:
            self.tile_position = kwargs["tile_position"]

    # =========================================================================

    @property
    def position(self):
        # type: () -> dict
        """The position of the entity.

        The position of the entity in. Positions of most entities are located
        at their center, which can either be in the middle of a tile or it's
        transition, depending on the entities `tile_width` and `tile_height`.
        """
        return self._position

    @position.setter
    def position(self, value):
        # type: (Union[dict, list, tuple]) -> None
        try:
            self._position = {"x": float(value["x"]), "y": float(value["y"])}
        except TypeError:
            self._position = {"x": float(value[0]), "y": float(value[1])}

        grid_x = round(self._position["x"] - self._tile_width / 2.0)
        grid_y = round(self._position["y"] - self._tile_height / 2.0)
        self._tile_position = {"x": grid_x, "y": grid_y}

        # if the grid alignment is off, warn the user
        if self._tile_position["x"] % 2 == 1 or self._tile_position["y"] % 2 == 1:
            cast_position = [
                math.floor(self._tile_position["x"] / 2) * 2,
                math.floor(self._tile_position["y"] / 2) * 2,
            ]
            warnings.warn(
                "Double-grid aligned entity is not placed along chunk grid; "
                "entity's position will be cast from {} to {} when imported".format(
                    self._tile_position, cast_position
                ),
                RailAlignmentWarning,
                stacklevel=2,
            )

    # =========================================================================

    @property
    def tile_position(self):
        # type: () -> dict
        """The tile-position of the Entity.

        `tile_position` is the position according to the LuaSurface tile grid,
        and is represented as integers

        Overwritten
        """
        return self._tile_position

    @tile_position.setter
    def tile_position(self, value):
        # type: (Union[dict, list, tuple]) -> None
        try:
            self._tile_position = {
                "x": math.floor(value["x"]),
                "y": math.floor(value["y"]),
            }
        except TypeError:
            self._tile_position = {"x": math.floor(value[0]), "y": math.floor(value[1])}

        absolute_x = self._tile_position["x"] + self._tile_width / 2.0
        absolute_y = self._tile_position["y"] + self._tile_height / 2.0
        self._position = {"x": absolute_x, "y": absolute_y}

        # if the grid alignment is off, warn the user
        if self._tile_position["x"] % 2 == 1 or self._tile_position["y"] % 2 == 1:
            cast_position = [
                math.floor(self._tile_position["x"] / 2) * 2,
                math.floor(self._tile_position["y"] / 2) * 2,
            ]
            warnings.warn(
                "Double-grid aligned entity is not placed along chunk grid; "
                "entity's position will be cast from {} to {} when imported".format(
                    self._tile_position, cast_position
                ),
                RailAlignmentWarning,
                stacklevel=2,
            )
