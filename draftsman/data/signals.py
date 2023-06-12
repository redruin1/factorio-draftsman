# signals.py

from __future__ import unicode_literals

from draftsman import data
from draftsman.data import entities, modules
from draftsman.error import InvalidSignalError, InvalidMappingError

import pickle
import six

try:  # pragma: no coverage
    import importlib.resources as pkg_resources  # type: ignore
except ImportError:  # pragma: no coverage
    # Try backported to PY<37 `importlib_resources`.
    import importlib_resources as pkg_resources  # type: ignore


with pkg_resources.open_binary(data, "signals.pkl") as inp:
    _data = pickle.load(inp)
    raw = _data[0]
    type_of = _data[1]
    item = _data[2]
    fluid = _data[3]
    virtual = _data[4]
    pure_virtual = ["signal-everything", "signal-anything", "signal-each"]


def add_signal(name, type):
    # type: (str, str) -> None
    """
    Temporarily adds a signal to :py:mod:`draftsman.data.signals`. This allows
    the user to specify custom signals so that Draftsman can deduce their type
    without having to install a corresponding mod. More specifically, it
    populates :py:data:`raw` and :py:data:`type_of` with the correct values,
    and adds the name to either :py:data:`item`, :py:data:`fluid`, or
    :py:data:`virtual` depending on ``type``.

    Note that this is not intended as a replacement for generating proper signal
    data using ``draftsman-update``; instead it offers a fast mechanism for
    emulating a custom signal and being able to only specify it by it's string
    shorthand, instead of it's full ``{"name": ..., "type": ...}`` format.

    :raises ValueError: If ``type`` is not set to one of ``"item"``, ``"fluid"``
        or ``"virtual"``.

    :param name: The in-game string ID of the signal.
    :param type: The signal-dict type of the signal.
    """
    if type not in {"item", "fluid", "virtual"}:
        raise ValueError("Signal type must be one of 'item', 'fluid', or 'virtual'")

    raw[name] = {"name": name, "type": type}
    type_of[name] = type
    if type == "item":
        item.append(name)
    elif type == "fluid":
        fluid.append(name)
    else:  # type == "virtual":
        virtual.append(name)


def get_signal_type(signal_name):
    # type: (str) -> str
    """
    Returns the type of the signal based on its ID string.

    SignalID objects in blueprints require a ``"type"`` field when specifying
    them. However, this information is redundant most of the time, as the type
    for any signal is always the same, making writing it out arduous. This
    function conveniently gets the signal type from the signal's name.

    :param signal_name: The name of the signal.
    :returns: One of ``"item"``, ``"fluid"``, or ``"virtual"``.
    :exception InvalidSignalError: If the signal name is not contained within
        :py:mod:`draftsman.data.signals`, and thus it's type cannot be deduced.
    """
    # if signal_name in signals.virtual:
    #     return "virtual"
    # elif signal_name in signals.fluid:
    #     return "fluid"
    # elif signal_name in signals.item:
    #     return "item"
    # else:
    #     raise InvalidSignalError("'{}'".format(str(signal_name)))

    try:
        return six.text_type(type_of[signal_name])
    except KeyError:
        raise InvalidSignalError("'{}'".format(signal_name))


def signal_dict(signal_name):
    # type: (str) -> dict
    """
    Creates a SignalID ``dict`` from the given signal name.

    Uses :py:func:`get_signal_type` to get the type for the dictionary.

    :param signal_name: The name of the signal.

    :returns: A dict with the ``"name"`` and ``"type"`` keys set.
    """
    return {"name": six.text_type(signal_name), "type": get_signal_type(signal_name)}


def get_mapping_type(mapping_name):
    # type: (str) -> str
    """
    TODO
    """
    # TODO: actually check that this is the case (particularly with modded entities/items)
    if mapping_name in modules.raw:  # TODO: should probably change
        return "item"
    elif mapping_name in entities.raw:  # TODO: should probably change
        return "entity"
    else:
        raise InvalidMappingError("'{}'".format(mapping_name))


def mapping_dict(mapping_name):
    # type: (str) -> dict
    """
    Creates a MappingID ``dict`` from  the given mapping name.

    TODO
    """
    return {"name": six.text_type(mapping_name), "type": get_mapping_type(mapping_name)}
