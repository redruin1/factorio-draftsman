# tiles.py

import pickle

import importlib.resources as pkg_resources

from draftsman import data


with pkg_resources.files(data).joinpath("tiles.pkl").open("rb") as inp:
    raw: dict[str, dict] = pickle.load(inp)


def add_tile(name: str, collision_mask: set[str] = set()):
    """
    Temporarily adds a tile to :py:mod:`draftsman.data.tiles`.

    :param name: The tile's Factorio ID.
    :param collision_mask: A set of strings, where each string represents a
        collision layer that this tile collides with.
    """
    raw[name] = {"name": name, "collision_mask": collision_mask}
