import pickle

import importlib.resources as pkg_resources

from draftsman import data

try:
    with pkg_resources.open_binary(data, "equipment.pkl") as inp:
        _data = pickle.load(inp)
        grids: dict[str, dict] = _data[0]

except FileNotFoundError:  # pragma: no coverage
    grids: dict[str, dict] = {}
