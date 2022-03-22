# tile.py

from draftsman.error import InvalidTileError

import draftsman.data.tiles as tiles


class Tile(object):
    """
    """
    def __init__(self, name, x = 0, y = 0):
        # type: (str, int, int) -> None
        if name not in tiles.raw:
            raise InvalidTileError("'{}'".format(str(name)))
        # TODO: validate
        self.name = name
        # Tile positions are in grid coordinates
        self.set_position(x, y)
        # Tile aabb for SpatialHashMap
        self.collision_box = [[0, 0], [1, 1]]

    def set_name(self, new_name):
        # type: (str) -> None
        if new_name not in tiles.raw:
            raise InvalidTileError("'{}'".format(str(new_name)))
        self.name = new_name

    def set_position(self, x, y):
        # type: (int, int) -> None
        # TODO swap this to self.position like entity
        # maybe make a vector class with .x and .y that converts to dict?
        # self.x = x
        # self.y = y
        self.position = {"x": x, "y": y}

    def get_area(self):
        # type: () -> list
        """
        Gets the world-space coordinate AABB of the tile.
        """
        return [[self.collision_box[0][0] + self.position["x"],
                 self.collision_box[0][1] + self.position["y"]],
                [self.collision_box[1][0] + self.position["x"],
                 self.collision_box[1][1] + self.position["y"]]]

    def to_dict(self):
        # type: () -> dict
        return {"name": self.name, "position": self.position}

    def __repr__(self):
        return "<Tile>" + str(self.to_dict())
