# tile.py

from .errors import InvalidTileID
from .tile_data import tile_names


class Tile:
    def __init__(self, name: str, x: int = 0, y: int = 0):
        if name not in tile_names:
            raise InvalidTileID("'" + str(name) + "'")
        # TODO: validate
        self.name = name
        # Tile positions are in grid coordinates
        self.set_position(x, y)

    def change_name(self, new_name: str) -> None:
        if new_name not in tile_names:
            raise InvalidTileID("'" + str(new_name) + "'")
        self.name = new_name

    def set_position(self, x: int, y: int) -> None:
        #self.position = {"x": x, "y": y}
        self.x = x
        self.y = y

    def to_dict(self) -> dict:
        return {"name": self.name, "position": {"x": self.x, "y": self.y}}

    def __repr__(self):
        return "<Tile>" + str(self.to_dict())
