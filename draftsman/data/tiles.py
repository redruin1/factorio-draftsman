# tiles.py

import pickle

from importlib.resources import files

from draftsman import data


try:
    source = files(data) / "tiles.pkl"
    with source.open("rb") as inp:
        raw: dict[str, dict] = pickle.load(inp)

except FileNotFoundError:  # pragma: no coverage
    raw = {}


def add_tile(name: str, collision_mask: set[str] = set()):
    """
    Temporarily adds a tile to :py:mod:`draftsman.data.tiles`.

    :param name: The tile's Factorio ID.
    :param collision_mask: A set of strings, where each string represents a
        collision layer that this tile collides with.
    """
    raw[name] = {"name": name, "collision_mask": collision_mask}
