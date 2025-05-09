# recipes.py

import pickle
import math

import importlib.resources as pkg_resources

# from draftsman import data
from .. import data

from draftsman.data.planets import get_surface_properties
from draftsman.utils import passes_surface_conditions


with pkg_resources.open_binary(data, "recipes.pkl") as inp:
    _data = pickle.load(inp)
    raw: dict[str, dict] = _data[0]
    categories: dict[str, list[str]] = _data[1]
    for_machine: dict[str, list[str]] = _data[2]


def add_recipe(name: str, ingredients: list[str], result: str, **kwargs):
    raise NotImplementedError  # TODO


def get_recipe_ingredients(recipe_name: str, expensive: bool = False):
    """
    Returns a ``set`` of all item types that ``recipe_name`` requires. Discards
    quantities.

    First attempts to get the ``"ingredients"`` key from the recipe. If that
    fails, we then attempt to get the contents of the ``"normal"`` key from
    recipe (which is the list of ingredients under non-expensive map settings).

    :param recipe_name: The name of the recipe to get the ingredients of.
    :param expensive: Whether or not to return the expensive recipe if available.
        If not, defaults to the normal recipe requirements.

    :returns: A ``set`` of names of each Factorio item that the recipe requires.

    :exception KeyError: If ``recipe_name`` is not a valid recipe.

    :example:

    .. code-block:: python

        print(recipes.get_recipe_ingredients("electronic-circuit"))
        # {'iron-plate', 'copper-cable'}

    """
    if recipe_name is None or recipe_name not in raw:
        return None
    if "ingredients" in raw[recipe_name]:
        return {
            x[0] if isinstance(x, list) else x["name"]
            for x in raw[recipe_name]["ingredients"]
        }
    else:  # recipe has two costs, "normal" and "expensive"
        cost_type = "expensive" if expensive else "normal"
        return {
            x[0] if isinstance(x, list) else x["name"]
            for x in raw[recipe_name][cost_type]["ingredients"]
        }


def is_usable_on(recipe_name: str, surface_name: str) -> bool:
    """
    Determines whether
    """
    recipe = raw[recipe_name]
    if "surface_conditions" not in recipe:
        return True

    surface_properties = get_surface_properties(surface_name)
    return passes_surface_conditions(recipe["surface_conditions"], surface_properties)
