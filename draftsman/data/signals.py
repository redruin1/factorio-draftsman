# signals.py
# -*- encoding: utf-8 -*-

from __future__ import unicode_literals

from draftsman import data
from draftsman.error import InvalidSignalError

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


def get_signal_type(signal_name):
    # type: (str) -> str
    """
    Returns the type of the signal based on its ID string.

    SignalID objects in blueprints require a ``"type"`` field when specifying
    them. However, this information is redundant most of the time, as the type
    for any signal is always the same, making writing it out arduous. This
    function conveniently gets the signal type from the signal's name.

    :param signal_name: The name of the signal.
    :returns: ``"item"``, ``"fluid"``, or ``"virtual"``
    :exception InvalidSignalError: If the signal name is not contained within
        :py:mod:`draftsman.data.signals`.
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
