# mods.py

import pickle

import importlib.resources as pkg_resources

from draftsman import data


with pkg_resources.open_binary(data, "mods.pkl") as inp:
    mod_list: dict[str, tuple] = pickle.load(inp)
