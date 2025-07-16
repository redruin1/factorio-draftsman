# qualities.py

import pickle

from importlib.resources import files
from draftsman import data


try:
    source = files(data) / "qualities.pkl"
    with source.open("rb") as inp:
        _data = pickle.load(inp)
        raw: dict[str, dict] = _data[0]

except FileNotFoundError:  # pragma: no coverage
    raw: dict[str, dict] = {}
