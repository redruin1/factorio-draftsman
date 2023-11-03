# instruments.py

import pickle

try:  # pragma: no coverage
    import importlib.resources as pkg_resources  # type: ignore
except ImportError:  # pragma: no coverage
    # Try backported to PY<37 `importlib_resources`.
    import importlib_resources as pkg_resources  # type: ignore

from draftsman import data


with pkg_resources.open_binary(data, "instruments.pkl") as inp:
    _data: list = pickle.load(inp)
    raw: dict[str, list[dict]] = _data[0]
    index: dict[str, dict[str, dict[str, int]]] = _data[1]
    names: dict[str, dict[int, dict[int, str]]] = _data[2]


def add_instrument(entity: str, name: str, notes: list[str]):
    raise NotImplementedError
