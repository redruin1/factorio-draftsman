# recipes.py

import pickle

import importlib.resources as pkg_resources

# from draftsman import data
from .. import data


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

    .. NOTE::

        Assumes that the items required for 'normal' mode are the same as
        'expensive' mode. This is unlikely true under all circumstances, but how
        will we issue warnings for invalid item requests if we dont know what
        mode the world save is in?

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
