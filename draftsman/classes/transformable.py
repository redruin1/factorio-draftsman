# transformable.py
# -*- encoding: utf-8 -*-

from draftsman.error import RotationError, FlippingError
from draftsman.warning import RailAlignmentWarning, FlippingWarning

import warnings


class Transformable(object):
    """
    Implements a number of functions that allow the parent class to spatially
    transform its ``entities`` and ``tiles`` lists. All of the following methods
    operate in-place, meaning that the original positions and directions of
    every entity and tile are modified each time they are called.
    """

    def translate(self, x, y):
        # type: (int, int) -> None
        """
        Translates all entities and tiles in the blueprint by ``x`` and ``y``.
        Raises :py:class:`~draftsman.warning.RailAlignmentWarning` if the
        parent class contains double-grid-aligned entities and the translation
        amount is an odd value on either x or y.

        :param x: A number indicating how much to translate along x.
        :param y: A number indicating how much to translate along y.
        """
        # Warn if attempting to translate by an odd amount when containing
        # double-grid-aligned entities
        if self.double_grid_aligned and (x % 2 == 1 or y % 2 == 1):
            warnings.warn(
                "Attempting to translate an odd number of tiles when this "
                "Transformable contains double grid-aligned entities; Their "
                "positions will be cast to the nearest grid square on export",
                RailAlignmentWarning,
                stacklevel=2,
            )

        # Entities
        for entity in self.entities:
            # Remove from hashmap
            self.entity_hashmap.remove(entity)

            entity._parent = None

            # Change entity position
            entity.position = (entity.position["x"] + x, entity.position["y"] + y)

            entity._parent = self

            # Re-add to hashmap
            self.entity_hashmap.add(entity)

        # Tiles
        if hasattr(self, "tiles"):
            for tile in self.tiles:
                # Remove from hashmap
                self.tile_hashmap.remove(tile)

                tile._parent = None

                # Change entity position
                tile.position["x"] += x
                tile.position["y"] += y

                tile._parent = self

                # Re-add to hashmap
                self.tile_hashmap.add(tile)

        self.recalculate_area()

    def rotate(self, angle):
        # type: (int) -> None
        """
        Rotate the blueprint by ``angle``, if possible. Operates the same as
        pressing 'r' with a blueprint selected.

        ``angle`` is specified in terms of Direction enum, meaning that a
        rotation of 2 is 90 degrees clockwise.

        Because eight-way rotatable entities exist in a weird gray area, this
        function behaves like the feature in-game and only rotates on 90 degree
        intervals. Attempting to rotate the blueprint an odd amount raises
        an :py:class:`~draftsman.error.RotationError`.

        .. WARNING::

            **This function is currently under active development.**

        :param angle: The angle to rotate the blueprint by.

        :exception RotationError: If the rotation is attempted with an odd
            value.
        """
        # TODO: handle different origin locations
        angle = angle % 8

        if angle % 2 == 1:
            raise RotationError("Blueprints cannot be rotated by an odd number")

        matrices = {
            0: [1, 0, 0, 1],
            2: [0, 1, -1, 0],
            4: [-1, 0, 0, -1],
            6: [0, -1, 1, 0],
        }
        matrix = matrices[angle]

        # Entities
        for entity in self.entities:
            # Remove from hashmap
            self.entity_hashmap.remove(entity)

            # Make a (separate!) copy of the position to transform
            pos = [entity.position["x"], entity.position["y"]]

            entity._parent = None

            # Alter the direction
            if entity.rotatable:
                entity.direction += angle
            # Alter (both) the position(s)
            entity.position = (
                pos[0] * matrix[0] + pos[1] * matrix[2],
                pos[0] * matrix[1] + pos[1] * matrix[3],
            )

            entity._parent = self

            # Re-add to hashmap
            self.entity_hashmap.add(entity)

        # Tiles
        if hasattr(self, "tiles"):
            for tile in self.tiles:
                # Remove from hashmap
                self.tile_hashmap.remove(tile)

                tile._parent = None

                # Make a (separate!) copy of the position to transform
                # With tiles we rotate from their center
                pos = [tile.position["x"] + 0.5, tile.position["y"] + 0.5]
                # Alter the position
                tile.position = (
                    pos[0] * matrix[0] + pos[1] * matrix[2] - 0.5,
                    pos[0] * matrix[1] + pos[1] * matrix[3] - 0.5,
                )

                tile._parent = self

                # Re-add to hashmap
                self.tile_hashmap.add(tile)

        self.recalculate_area()

    def flip(self, direction="horizontal"):
        # type: (str) -> None
        """
        Flip the blueprint across an axis, if possible. Flipping is done over
        the x or y axis, depeding on the input ``direction``.

        .. WARNING::

            **This function is currently under active development.**

        :param direction: The direction to flip by; either ``"horizontal"`` or
            ``"vertical"``
        """
        # TODO: handle different axis locations

        # Issue an error if attempting to flip a collection that has unflippable
        # entities
        if not self.flippable:
            raise FlippingError("Blueprint cannot be flipped")

        # TODO: determine what entities are modded or not
        # if self.contains_modded_entities:
        #     warnings.warn(
        #         "Flipping the blueprint is not guaranteed to work when it has "
        #         "modded entities inside it; proceed with caution",
        #         FlippingWarning,
        #         stacklevel=2
        #     )

        if direction not in {"horizontal", "vertical"}:
            raise ValueError("'direction' must be either 'horizontal' or 'vertical'")

        matrices = {"horizontal": [-1, +1], "vertical": [+1, -1]}
        matrix = matrices[direction]

        # Entities
        for entity in self.entities:
            # Remove from hashmap
            self.entity_hashmap.remove(entity)

            entity._parent = None

            # Make a (separate!) copy of the position to transform
            pos = [entity.position["x"], entity.position["y"]]
            # Alter the direction
            if entity.rotatable:
                if direction == "horizontal":
                    entity.direction += ((-2 * (entity.direction - 4)) % 8) % 8
                else:  # direction == "vertical":
                    entity.direction += (((-2 * entity.direction) % 8) - 4) % 8

            # Alter (both) the position(s)
            entity.position = (pos[0] * matrix[0], pos[1] * matrix[1])

            entity._parent = self

            # Re-add to hashmap
            self.entity_hashmap.add(entity)

        # Tiles
        if hasattr(self, "tiles"):
            for tile in self.tiles:
                # Remove from hashmap
                self.tile_hashmap.remove(tile)

                tile._parent = None

                # Make a (separate!) copy of the position to transform
                # With tiles we flip from their center
                pos = [tile.position["x"] + 0.5, tile.position["y"] + 0.5]
                # Alter the position
                tile.position = (pos[0] * matrix[0] - 0.5, pos[1] * matrix[1] - 0.5)

                tile._parent = self

                # Re-add to hashmap
                self.tile_hashmap.add(tile)

        self.recalculate_area()
