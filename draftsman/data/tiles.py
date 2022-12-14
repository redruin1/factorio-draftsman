# tiles.py

import pickle

try:  # pragma: no coverage
    import importlib.resources as pkg_resources  # type: ignore
except ImportError:  # pragma: no coverage
    # Try backported to PY<37 `importlib_resources`.
    import importlib_resources as pkg_resources  # type: ignore

from draftsman import data


with pkg_resources.open_binary(data, "tiles.pkl") as inp:
    raw = pickle.load(inp)


def add_tile(name, collision_mask=set()):
    # type: (str, set[str]) -> None
    """
    Temporarily adds a tile to :py:mod:`draftsman.data.tiles`.

    :param name: The tile's Factorio ID.
    :param collision_mask: A set of strings, where each string represents a
        collision layer that this tile collides with.
    """
    raw[name] = {"collision_mask": collision_mask}
