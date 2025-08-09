# mods.py

import pickle

from importlib.resources import files

from draftsman import data


try:
    source = files(data) / "mods.pkl"
    with source.open("rb") as inp:
        versions: dict[str, tuple] = pickle.load(inp)

except FileNotFoundError:  # pragma: no coverage
    versions = {}
