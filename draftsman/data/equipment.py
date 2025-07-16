import pickle

from importlib.resources import files

from draftsman import data

try:
    source = files(data) / "equipment.pkl"
    with source.open("rb") as inp:
        _data = pickle.load(inp)
        grids: dict[str, dict] = _data[0]

except FileNotFoundError:  # pragma: no coverage
    grids: dict[str, dict] = {}
