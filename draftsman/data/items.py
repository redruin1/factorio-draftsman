# items.py

import pickle

from importlib.resources import files

from draftsman import data
from draftsman.data import recipes

from math import floor
from typing import Optional


try:
    source = files(data) / "items.pkl"
    with source.open("rb") as inp:
        _data = pickle.load(inp)
        raw: dict[str, dict] = _data[0]
        subgroups: dict[str, dict] = _data[1]
        groups: dict[str, dict] = _data[2]
        fuels: dict[str, set[str]] = _data[3]
        all_fuel_items: set[str] = set(
            item for category in fuels for item in fuels[category]
        )

except FileNotFoundError:  # pragma: no coverage
    pass


def add_group(name: str, order: str = "", subgroups=[], **kwargs):
    """
    Adds a new item group to Draftsman's environment, which persists until the
    end of the session.
    """
    # Prioritize existing data if present
    existing_data = raw.get(name, {})
    order = existing_data.get("order", order)
    # items = existing_data.get("subgroups", subgroups)
    # Assign
    new_data = {
        **existing_data,
        "type": "item-group",
        "name": name,
        "order": order,
        "subgroups": subgroups,
        **kwargs,
    }
    # TODO: sorted insert
    # This is harder than it sounds though
    groups[name] = new_data


def add_subgroup(name: str, group: str, items=[], order: str = "", **kwargs):
    """
    Adds a new item subgroup to Draftsman's environment, which persists until
    the end of the session.
    """
    # Prioritize existing data if present
    existing_data = raw.get(name, {})
    order = existing_data.get("order", order)
    items = existing_data.get("items", items)
    # Assign
    new_data = {
        **existing_data,
        "type": "item-subgroup",
        "name": name,
        "order": order,
        "items": items,
        **kwargs,
    }

    if group not in groups:
        raise TypeError(
            "Unknown item group '{}'; if you want to add a new item group, call `items.add_group(name='{}', ...)`"
        )
    else:
        # TODO: sorted insert
        # This is harder than it sounds though
        subgroups[name] = new_data
        groups[group]["subgroups"].append(new_data)


def add_item(
    name: str, stack_size: int, order: str = "", subgroup: str = "other", **kwargs
):
    """
    Add a new item, or modify the properties of an existing item. Useful for
    simulating a modded environment without having to fully supply an entire
    mod configuration for simple scripts.

    If you specify a subgroup name that does not exist in `items.subgroups`,
    then this function will create a new item subgroup and populate this dict
    as well with a dummy value.

    If you want to add an item to custom groups, it likely makes more sense to
    run the functions `items.add_group` and `items.add_subgroup` with the
    data you want before calling this function.

    Any modifications to the environment only persist for the remainder of that
    session.
    """
    # Prioritize existing data if present
    existing_data = raw.get(name, {})
    order = existing_data.get("order", order)
    subgroup = existing_data.get("subgroup", subgroup)
    # Assign
    new_data = {
        **existing_data,
        "type": "item",
        "name": name,
        "stack_size": stack_size,
        "order": order,
        "subgroup": subgroup,
        **kwargs,
    }

    if subgroup not in subgroups:
        raise TypeError(
            "Unknown item subgroup '{}'; if you want to add a new item subgroup, call `items.add_subgroup(name='{}', ...)`"
        )
    else:
        # TODO: sorted insert
        # This is harder than it sounds though
        raw[name] = new_data
        subgroups[subgroup]["items"].append(new_data)

    # TODO: this should also update signals


def get_stack_size(item_name: str) -> int:
    """
    Returns the stack size of the associated item. If ``item_name`` is not
    recognized as a known item, then this function returns ``None``.

    :param item_name: The name of the item to get the stack size from.
    :returns: The amount of this item that can fit inside a single inventory
        slot.
    """
    return raw.get(item_name, {"stack_size": None})["stack_size"]


# TODO: this should be pulled from `utility-constants.lua`
DEFAULT_ITEM_WEIGHT = 100.0
ROCKET_LIFT_WEIGHT = 1_000_000.0


def get_weight(
    item_name: str, already_visited: Optional[set] = None
) -> Optional[float]:
    """
    Gets the weight of the item, as specified by the algorithm here:
    :ref:`https://lua-api.factorio.com/latest/auxiliary/item-weight.html`

    If this item is not recognized by Draftsman, this function returns ``None``
    instead.

    :param item_name: The name of the item.
    :param already_visited: Whether or not this particular item has already been
        calculated in a recursive call to ``get_weight``. The caller should
        always keep this argument ``None``.

    :returns: The weight of the item in kilograms, or ``None`` if unable to
        determine the item's weight.
    """
    # We need to construct a set of items already visted in order to terminate
    # recipe loops if they appear
    if already_visited is None:
        already_visited = set()

    # If we don't recognize the item, we cannot determine the item's weight
    if item_name not in raw:
        # Shouldn't ever reach here in recursive case, since recipes should only
        # ever point to items they know about
        return None

    # If the weight is manually specified, obviously use that:
    if "weight" in raw[item_name]:
        return raw[item_name]["weight"]

    # "If this results in a recipe loop, it will fall back to the default item
    # weight for that item."
    if item_name in already_visited:
        return DEFAULT_ITEM_WEIGHT
    already_visited.add(item_name)

    # "If an item has the `"only-in-cursor"` and `"spawnable"` flags, its weight
    # will be 0."
    item_flags = raw[item_name].get("flags", [])
    if "only-in-cursor" in item_flags and "spawnable" in item_flags:
        return 0.0

    # "The game starts by calculating the 'recipe weight' of the item's recipe."
    # "Note that recipes that are hidden or don't allow_decomposition are not
    # considered for this use case."
    recipe_weight = 0.0
    recipes_that_produces_item = [
        recipe
        for recipe in recipes.raw.values()
        if item_name in {result["name"] for result in recipe.get("results", [])}
        and "hidden" not in recipe
        and recipe.get("allow_decomposition", True)
    ]

    # "If an item has no recipe to produce it, it'll fall back to the default
    # item weight."
    if len(recipes_that_produces_item) == 0:
        return DEFAULT_ITEM_WEIGHT

    # "If an item has multiple recipes, it picks the first recipe, according to
    # the sorting:
    #  * The name of the recipe is identical to the item name.
    #  * The recipe is not using the item as a catalyst.
    #  * The recipe can be used as an intermediate while hand-crafting.
    #  * The recipe's category, subgroup, then order.
    # "
    recipe = sorted(
        recipes_that_produces_item,
        key=lambda x: (
            # Sort the first 3 descending (True, then False)
            not (x["name"] == item_name),
            not (item_name not in {product["name"] for product in x["results"]}),
            not (x.get("allow_as_intermediate", True)),
            # And the last 3 ascending (a -> z)
            x.get("category", "crafting"),
            x.get("subgroup", ""),
            x.get("order", ""),
        ),
    )[0]

    for ingredient in recipe["ingredients"]:
        if ingredient["type"] == "item":
            # "For each item ingredient, the weight is increased by:
            #   item_weight * item_ingredient_count"
            item_weight = get_weight(ingredient["name"], already_visited)
            recipe_weight += item_weight * ingredient["amount"]
        else:  # ingredient["type"] == "fluid":
            # "For each fluid ingredient, the weight is increased by:
            #   fluid_ingredient_amount * 100"
            recipe_weight += ingredient["amount"] * 100

    # "If the resulting recipe_weight is 0, the item's weight will fall back to
    # the default item weight."
    if recipe_weight == 0.0:  # pragma: no coverage
        return DEFAULT_ITEM_WEIGHT

    # "The game then determines the product count of the recipe by iterating all
    # products and adding up the expected (ie. after probabilities) count for
    # all item products. Fluid products are skipped."
    product_count = 0
    for product in recipe["results"]:
        if product["type"] == "item":  # pragma: no branch
            # TODO: handle probabilities
            product_count += product["amount"]

    # "If the recipe's product count is 0, the item's weight will fall back to
    # the default item weight."
    if product_count == 0:  # pragma: no coverage
        return DEFAULT_ITEM_WEIGHT

    # "Next, an intermediate result will be determined as:
    #   (recipe_weight / product_count) * ingredient_to_weight_coefficient
    # (see ingredient_to_weight_coefficient, which defaults to 0.5)."
    weight_coef = raw[item_name].get("ingredient_to_weight_coefficient", 0.5)
    intermediate_result = (recipe_weight / product_count) * weight_coef

    # "Following this, if a recipe doesn't support productivity, its simple
    # result is determined as:
    #   rocket_lift_weight / stack_size"
    stack_size = get_stack_size(item_name)
    if not recipe.get("allow_productivity", False):
        simple_result = ROCKET_LIFT_WEIGHT / stack_size

        # "If this simple result is larger than or equal to the intermediate result,
        # it becomes the item's weight."
        if simple_result >= intermediate_result:  # pragma: no branch
            return simple_result

    # "Otherwise, the game determines the amount of stacks that would result
    # from the intermediate result as:
    #   rocket_lift_weight / intermediate_result / stack_size
    stack_amount = ROCKET_LIFT_WEIGHT / intermediate_result / stack_size

    if stack_amount <= 1:  # pragma: no coverage
        # " If this amount is less than or equal to 1, the intermediate result
        # becomes the item's weight."
        return intermediate_result
    else:
        # "Else, the item's weight is set to:
        #   rocket_lift_weight / floor(stack_amount) / stack_size."
        return ROCKET_LIFT_WEIGHT / floor(stack_amount) / stack_size
