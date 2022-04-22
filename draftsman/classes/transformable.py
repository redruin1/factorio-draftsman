# transformable.py

from draftsman.error import RotationError, FlippingError
from draftsman.warning import RailAlignmentWarning

import warnings


class Transformable(object):
    """
    Allows a collection of entities to translate, rotate, and flip. Operates
    on the `entities` EntityList, the `tiles` TileList, and the `entity_hashmap`
    and `tile_hashmap` SpatialHashMaps respectively.
    """

    def translate(self, x, y):
        # type: (int, int) -> None
        """
        Translates all entities and tiles in the blueprint by an amount.
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
        Rotate the blueprint by `angle`, if possible. Operates the same as
        pressing 'r' with a blueprint selected.
        ``angle`` is specified in terms of Direction Enum, meaning that a
        rotation of 2 is 90 degrees clockwise.
        Because eight-way rotatable entities exist in a weird gray area, this
        function behaves like the feature in-game and only rotates on 90 degree
        intervals. Attempting to rotate the blueprint an odd amount raises
        an :py:class:`draftsman.error.RotationError`.
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
        # type: (str, float) -> None
        """
        Flip the blueprint across `axis`, if possible.

        .. WARNING::

            **This function is not "Factorio-safe" and is currently under
            development.** The function still operates, though it will not
            throw ``BlueprintFlippingError`` when the blueprint contains
            entities that cannot be flipped, which may break some blueprints.
            Proceed with caution.
        """
        # TODO: handle different axis locations
        # Prevent the blueprint from being flipped if it contains entities that
        # cannot be flipped
        # if not self.flippable:
        #     raise BlueprintFlippingError("Blueprint cannot be flipped")

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
