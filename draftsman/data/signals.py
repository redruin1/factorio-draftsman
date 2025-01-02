# signals.py

from draftsman import data
from draftsman.data import entities, modules
from draftsman.error import InvalidSignalError, InvalidMapperError

import pickle

import importlib.resources as pkg_resources


with pkg_resources.open_binary(data, "signals.pkl") as inp:
    _data = pickle.load(inp)

    raw: dict[str, dict] = _data["raw"]

    # Look up table for a particular signal's type
    type_of: dict[str, set[str]] = _data["type_of"]

    # Lists of signal names organized by their type for easy iteration
    virtual: list[str] = _data["virtual"]
    item: list[str] = _data["item"]
    fluid: list[str] = _data["fluid"]
    recipe: list[str] = _data["recipe"]
    entity: list[str] = _data["entity"]
    space_location: list[str] = _data["space-location"]
    asteroid_chunk: list[str] = _data["asteroid-chunk"]
    quality: list[str] = _data["quality"]
    # hidden: list[str] = _data["hidden"]
    pure_virtual: list[str] = ["signal-everything", "signal-anything", "signal-each"]


def add_signal(name: str, type: str):
    """
    Temporarily adds a signal to :py:mod:`draftsman.data.signals`. This allows
    the user to specify custom signals so that Draftsman can deduce their type
    without having to manually specify each time or install a corresponding mod.
    More specifically, it populates :py:data:`raw` and :py:data:`type_of` with
    the correct values, and adds the name to either :py:data:`.item`,
    :py:data:`.fluid`, or :py:data:`.virtual` depending on ``type``.

    Note that this is not intended as a replacement for generating proper signal
    data using ``draftsman-update``; instead it offers a fast mechanism for
    emulating a custom signal and being able to only specify it by it's string
    shorthand, instead of it's full ``{"name": ..., "type": ...}`` format.

    :raises ValueError: If ``type`` is not set to one of ``"item"``, ``"fluid"``
        or ``"virtual"``.

    :param name: The in-game string ID of the signal.
    :param type: The signal-dict type of the signal.
    """
    permitted_types = {
        "item",
        "fluid",
        "recipe",
        "entity",
        "space-location",
        "asteroid-chunk",
        "quality",
        "virtual",
    }
    if type not in permitted_types:
        raise ValueError("Signal type must be one of {}".format(permitted_types))

    raw[name] = {"name": name, "type": type}
    try:
        type_of[name].add(type)
    except KeyError:
        type_of[name] = {type}
    # TODO: sorting
    if type == "virtual":
        virtual.append(name)
    elif type == "item":
        item.append(name)
    elif type == "fluid":
        fluid.append(name)
    elif type == "recipe":
        recipe.append(name)
    elif type == "entity":
        entity.append(name)
    elif type == "space-location":
        space_location.append(name)
    elif type == "asteroid-chunk":
        asteroid_chunk.append(name)
    elif type == "quality":
        quality.append(name)


def get_signal_types(signal_name: str) -> set[str]:
    """
    Returns the set of types that a given signal can have based on its ID string.

    Typically, signals can only be selected with a single type, but the game
    distinguishes between signals of different types in the circuit network.
    This means that you can have multiple different versions of the "same"
    signal, with the only difference being their type. For example,
    ``transport-belt`` can have a type of ``"item"``, ``"recipe"``, or ``"entity"``.

    :param signal_name: The name of the signal.
    :returns: A set of strings that this signal's type can be.
    :exception InvalidSignalError: If the signal name is not contained within
        :py:mod:`draftsman.data.signals`, and thus it's types cannot be deduced.
    """
    try:
        return type_of[signal_name]
    except KeyError:
        raise InvalidSignalError("'{}'".format(signal_name))


def signal_dict(signal: str) -> dict:
    """
    Creates a SignalID ``dict`` from the given signal name.

    Uses :py:func:`get_signal_type` to get the type for the dictionary.

    :param signal_name: The name of the signal.

    :returns: A dict with the ``"name"`` and ``"type"`` keys set.
    :exception InvalidSignalError: If the signal name is not contained within
        :py:mod:`draftsman.data.signals`, and thus it's type cannot be deduced.
    """
    if signal is None or isinstance(signal, dict):
        return signal
    else:
        if "item" in get_signal_types(signal):
            return {"name": str(signal), "type": "item"}
        else:
            return {"name": str(signal), "type": next(iter(get_signal_types(signal)))}


def get_mapper_type(mapper_name: str) -> str:
    """
    TODO
    """
    # TODO: actually check that this is the case (particularly with modded entities/items)
    if mapper_name in modules.raw:  # TODO: should probably change
        return "item"
    elif mapper_name in entities.raw:  # TODO: should probably change
        return "entity"
    else:
        raise InvalidMapperError("'{}'".format(mapper_name))


def mapper_dict(mapper: str) -> dict:
    """
    Creates a MappingID ``dict`` from  the given mapping name.

    Uses :py:func:`get_mapping_type` to get the type for the dictionary.

    :param signal_name: The name of the signal.

    :returns: A dict with the ``"name"`` and ``"type"`` keys set.
    """
    if mapper is None or isinstance(mapper, dict):
        return mapper
    else:
        return {"name": str(mapper), "type": get_mapper_type(mapper)}
