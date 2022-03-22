# recipes.py

import pickle

try:
    import importlib.resources as pkg_resources # type: ignore
except ImportError:
    # Try backported to PY<37 `importlib_resources`.
    import importlib_resources as pkg_resources # type: ignore

from draftsman import data


with pkg_resources.open_binary(data, "recipes.pkl") as inp:
    _data = pickle.load(inp)
    raw = _data[0]
    categories = _data[1]
    for_machine = _data[2]