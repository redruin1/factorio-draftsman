# modules.py

import pickle

from importlib.resources import files

from draftsman import data, DEFAULT_FACTORIO_VERSION
from draftsman.data import recipes, mods

from typing import Optional


try:
    source = files(data) / "modules.pkl"
    with source.open("rb") as inp:
        _data = pickle.load(inp)
        raw: dict[str, dict] = _data[0]
        categories: dict[str, list[str]] = _data[1]

except FileNotFoundError:  # pragma: no coverage
    raw = {}
    categories = {}


def add_module_category(name: str, order: str = ""):
    """
    Creates a new category of modules in Draftsman's environment, which persists
    until the session ends.
    """
    # TODO: insert sorted
    categories[name] = []


def add_module(module_name: str, category_name: str, **kwargs):
    """
    Creates a module in Draftsman's environment, which persists until the
    session ends.
    """
    if category_name not in categories:
        raise TypeError(
            "Cannot add new module to unknown category '{}'".format(category_name)
        )

    existing_data = raw.get(module_name, {})
    effect = existing_data.get("effect", kwargs.pop("effect", {}))
    tier = existing_data.get("tier", kwargs.pop("tier", 0))
    # Add to `raw`
    new_entry = {
        **existing_data,
        "name": module_name,
        "category": category_name,
        "effect": effect,
        "tier": tier,
        **kwargs,
    }
    raw[module_name] = new_entry
    # Add to `categories`
    # TODO: insert sorted
    categories[category_name].append(module_name)


def get_modules_from_effects(
    allowed_effects: set[str], recipe_name: str = None
) -> Optional[set[str]]:
    """
    Given a set of string effect names, provide the set of available modules
    under the current Draftsman configuration that would fit in an entity with
    those effects. If a recipe is provided, limit the available modules to ones
    that can only be used with that recipe selected.
    """
    if allowed_effects is None:
        return None
    if recipe_name is not None:
        recipe = recipes.raw.get(recipe_name, None)
        if recipe is None:
            return None
    output = set()
    for module_name, module in raw.items():
        if recipe_name is not None:
            # Skip adding this module if the recipe provided does not fit within
            # this module's limitations
            factorio_version = mods.versions.get("base", (2, 0))
            if factorio_version < (2, 0):  # pragma: no coverage
                if "limitation" in module and recipe_name not in module["limitation"]:
                    continue
                elif (
                    "limitation_blacklist" in module
                    and recipe_name in module["limitation_blacklist"]
                ):
                    continue
            else:
                allowed_effects = {
                    effect
                    for effect, allowed in (
                        ("consumption", recipe.get("allow_consumption", True)),
                        ("speed", recipe.get("allow_speed", True)),
                        ("productivity", recipe.get("allow_productivity", False)),
                        ("pollution", recipe.get("allow_pollution", True)),
                        ("quality", recipe.get("allow_quality", True)),
                    )
                    if allowed
                }

        # I think the module's positive effects has to be a subset of the
        # set of allowed effects
        if mods.versions.get("base", DEFAULT_FACTORIO_VERSION) < (2, 0):
            positive_effects = {
                effect
                for effect, value in module["effect"].items()
                if value["bonus"] > 0
            }
        else:
            positive_effects = {
                effect for effect, value in module["effect"].items() if value > 0
            }

        if positive_effects.issubset(allowed_effects):
            output.add(module_name)

    return output
