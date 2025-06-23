# qualities.py

import pickle

import importlib.resources as pkg_resources
from draftsman import data


try:
    with pkg_resources.open_binary(data, "qualities.pkl") as inp:
        _data = pickle.load(inp)
        raw: dict[str, dict] = _data[0]

except FileNotFoundError:  # pragma: no coverage
    raw: dict[str, dict] = {}
