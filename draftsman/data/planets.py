# planets.py

import pickle

import importlib.resources as pkg_resources

from draftsman import data
from draftsman.classes.collision_set import CollisionSet
from draftsman.env import get_default_collision_mask
from draftsman.utils import PrimitiveAABB, AABB


try:
    with pkg_resources.files(data).joinpath("planets.pkl").open("rb") as inp:
        _data: dict = pickle.load(inp)

        raw: dict[str, dict] = _data[0]

except FileNotFoundError:
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
        return {
            "solar-power": surface.get("solar-power", 100),
            "magnetic-field": surface.get("magnetic-field", 90),
            "pressure": surface.get("pressure", 1000),
            "gravity": surface.get("gravity", 10),
        }
