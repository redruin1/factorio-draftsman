# recipes.py

import os
import pickle

try:  # pragma: no coverage
    import importlib.resources as pkg_resources  # type: ignore
except ImportError:  # pragma: no coverage
    # Try backported to PY<37 `importlib_resources`.
    import importlib_resources as pkg_resources  # type: ignore

# from draftsman import data
from .. import data


with pkg_resources.open_binary(data, "recipes.pkl") as inp:
    _data = pickle.load(inp)
    raw = _data[0]
    categories = _data[1]
    for_machine = _data[2]
