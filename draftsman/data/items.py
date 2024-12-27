# items.py

import pickle

import importlib.resources as pkg_resources

from draftsman import data


with pkg_resources.open_binary(data, "items.pkl") as inp:
    _data = pickle.load(inp)
    raw: dict[str, dict] = _data[0]
    subgroups: dict[str, dict] = _data[1]
    groups: dict[str, dict] = _data[2]
    fuels: dict[str, set[str]] = _data[3]
    all_fuel_items: set[str] = set(
        item for category in fuels for item in fuels[category]
    )


def add_group(name: str, order: str = "", subgroups=[], **kwargs):
    """
    TODO
    """
    # Prioritize existing data if present
    existing_data = raw.get(name, {})
    order = existing_data.get("order", order)
    items = existing_data.get("subgroups", subgroups)
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
    TODO
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
    as well with a dummy value. Note that this new subgroup will

    If you want to add an item to custom groups, it likely makes more sense to
    run the functions `items.add_group` and `items.add_subgroup` with the
    data you want before calling this function.

    Any modifications to the environment only persist for the remainder of that
    session.

    TODO
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


def get_weight(item_name: str) -> float:
    """
    TODO
    """
    return 0.0
