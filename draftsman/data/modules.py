# modules.py
# -*- encoding: utf-8 -*-

import pickle

try:  # pragma: no coverage
    import importlib.resources as pkg_resources  # type: ignore
except ImportError:  # pragma: no coverage
    # Try backported to PY<37 `importlib_resources`.
    import importlib_resources as pkg_resources  # type: ignore

from draftsman import data


with pkg_resources.open_binary(data, "modules.pkl") as inp:
    _data = pickle.load(inp)
    raw: dict[str, dict] = _data[0]
    categories: dict[str, list[str]] = _data[1]


def add_module(name: str, category: str):
    raise NotImplementedError


def get_modules_from_effects(allowed_effects: set[str], recipe: str = None) -> set[str]:
    """
    Given a list of string effect names, provide the list of available modules
    under the current Draftsman configuration that would fit in an entity with
    those effects.
    """
    if allowed_effects is None:
        return None
    output = set()
    for module_name, module in raw.items():
        if recipe is not None:
            # Skip addint this module if the recipe provided does not fit within
            # this module's limitations
            if "limitation" in module and recipe not in module["limitation"]:
                continue
            elif (
                "limitation_blacklist" in module
                and recipe in module["limitation_blacklist"]
            ):
                continue
        # I think the effects module has to be a subset of the allowed effects
        # in order to be included
        if set(module["effect"]).issubset(allowed_effects):
            output.add(module_name)

    return output
