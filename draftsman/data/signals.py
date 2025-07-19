# signals.py

from draftsman import data
from draftsman.data import entities, modules
from draftsman.error import InvalidSignalError, InvalidMapperError

import pickle
from typing import Literal

from importlib.resources import files


try:
    source = files(data) / "signals.pkl"
    with source.open("rb") as inp:
        _data = pickle.load(inp)

        raw: dict[str, dict] = _data["raw"]

        # Look up table for a particular signal's type
        type_of: dict[str, list[str]] = _data["type_of"]

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

except FileNotFoundError:  # pragma: no coverage
    raw = {}
    type_of = {}

    virtual = []
    item = []
    fluid = []
    recipe = []
    entity = []
    space_location = []
    asteroid_chunk = []
    quality = []

pure_virtual: list[str] = ["signal-everything", "signal-anything", "signal-each"]


def add_signal(name: str, type: str):
    """
    Temporarily adds a signal to :py:mod:`draftsman.data.signals`. This allows
    the user to specify custom signals so that Draftsman can deduce their type
    without having to manually specify each time or install a corresponding mod.
    More specifically, it populates :py:data:`raw` and :py:data:`type_of` with
    the correct values, and adds the name to the corresponding signal list of
    the specified type.

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
        "item": item,
        "fluid": fluid,
        "recipe": recipe,
        "entity": entity,
        "space-location": space_location,
        "asteroid-chunk": asteroid_chunk,
        "quality": quality,
        "virtual": virtual,
    }
    if type not in permitted_types:
        raise ValueError("Signal type must be one of {}".format(permitted_types))

    raw[name] = {"name": name, "type": type}
    try:
        type_of[name].append(type)
    except KeyError:
        type_of[name] = [type]
    # TODO: sorting
    permitted_types[type].append(name)


def get_signal_types(signal_name: str) -> list[str]:
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
        msg = "Cannot determine signal types for unknown signal '{}'".format(
            signal_name
        )
        raise InvalidSignalError(msg)


def get_mapper_type(mapper_name: str) -> Literal["item", "entity"]:
    """
    Determines which mapper type this object should be if specifying from a bare
    string.

    :returns: Either ``"item"`` if the input name was a module, or ``"entity"``
        if it is a known entity.
    :exception InvalidMapperError: If the input string was neither a known
        module nor a known entity (and thus the mapping type cannot be deduced).
    """
    if mapper_name in modules.raw:
        return "item"
    elif mapper_name in entities.raw:
        return "entity"
    else:
        raise InvalidMapperError("'{}'".format(mapper_name))


# def mapper_dict(mapper: str) -> dict:
#     """
#     Creates a MappingID ``dict`` from  the given mapping name.

#     Uses :py:func:`get_mapping_type` to get the type for the dictionary.

#     :param signal_name: The name of the signal.

#     :returns: A dict with the ``"name"`` and ``"type"`` keys set.
#     """
#     return {"name": str(mapper), "type": get_mapper_type(mapper)}
