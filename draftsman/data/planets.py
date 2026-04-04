# planets.py

import pickle

from importlib.resources import files

from draftsman import data


try:
    source = files(data) / "planets.pkl"
    with source.open("rb") as inp:
        _data: dict = pickle.load(inp)

        raw: dict[str, dict] = _data[0]

except FileNotFoundError:  # pragma: no coverage
    raw = {}


def get_surface_properties(surface_name: str) -> dict:
    """
    Returns a dictionary containing all surface properties of the specified
    surface. If entries for the surface are omitted, then defaults are supplied.
    If the surface is not recognized, then an empty dictionary is returned.
    """
    if surface_name not in raw:
        return {}
    else:
        surface = raw[surface_name]
        surface_props = surface.get("surface_properties", {})
        return {
            "solar-power": surface_props.get("solar-power", 100),
            "magnetic-field": surface_props.get("magnetic-field", 90),
            "pressure": surface_props.get("pressure", 1000),
            "gravity": surface_props.get("gravity", 10),
        }
