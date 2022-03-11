# tile.py

from draftsman.error import InvalidTileError

import draftsman.data.tiles as tiles


class Tile(object):
    def __init__(self, name, x = 0, y = 0):
        # type: (str, int, int) -> None
        if name not in tiles.raw:
            raise InvalidTileError("'{}'".format(str(name)))
        # TODO: validate
        self.name = name
        # Tile positions are in grid coordinates
        self.set_position(x, y)

    def set_name(self, new_name):
        # type: (str) -> None
        if new_name not in tiles.raw:
            raise InvalidTileError("'{}'".format(str(new_name)))
        self.name = new_name

    def set_position(self, x, y):
        # type: (int, int) -> None
        self.x = x
        self.y = y

    def to_dict(self):
        # type: () -> dict
        return {"name": self.name, "position": {"x": self.x, "y": self.y}}

    def __repr__(self):
        return "<Tile>" + str(self.to_dict())
