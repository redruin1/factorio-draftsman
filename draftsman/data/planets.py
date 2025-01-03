# planets.py

import pickle

import importlib.resources as pkg_resources

from draftsman import data
from draftsman.classes.collision_set import CollisionSet
from draftsman.env import get_default_collision_mask
from draftsman.utils import PrimitiveAABB, AABB


try:
    with pkg_resources.open_binary(data, "planets.pkl") as inp:
        _data: dict = pickle.load(inp)

        raw: dict[str, dict] = _data[0]

except FileNotFoundError:
    raw = {}
