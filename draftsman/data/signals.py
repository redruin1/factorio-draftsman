# signals.py

import pickle

try:  # pragma: no coverage
    import importlib.resources as pkg_resources  # type: ignore
except ImportError:  # pragma: no coverage
    # Try backported to PY<37 `importlib_resources`.
    import importlib_resources as pkg_resources  # type: ignore

from draftsman import data


with pkg_resources.open_binary(data, "signals.pkl") as inp:
    _data = pickle.load(inp)
    raw = _data[0]
    item = _data[1]
    fluid = _data[2]
    virtual = _data[3]
