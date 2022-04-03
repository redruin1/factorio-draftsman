# utils.py
# -*- encoding: utf-8 -*-

"""
Provides a number of common utility functions. These are primarily used 
internally by Draftsman, but can be useful outside of that scope and are 
provided to the user as-is.
"""

from __future__ import unicode_literals

from draftsman.error import MalformedBlueprintStringError, InvalidSignalError

from draftsman.data import recipes
from draftsman.data import signals

import base64
import json
import math
from functools import wraps
import six
from typing import Any
import warnings
import zlib


def string_to_JSON(string):
    # type: (str) -> dict
    """
    Decodes a Factorio Blueprint string to a readable JSON Dict.

    Follows the data format specification `here <https://wiki.factorio.com/Blueprint_string_format>`_.
    For the inverse operation, see :py:func:`JSON_to_string`.

    :param string: The input Factorio blueprint string.

    :returns: A JSON ``dict`` with the blueprint's components as keys.

    :exception MalformedBlueprintStringError: If the input string is not
        decodable to a JSON object.
    """
    try:
        return json.loads(zlib.decompress(base64.b64decode(string[1:])))
    except Exception:
        raise MalformedBlueprintStringError


def JSON_to_string(JSON):
    # type: (dict) -> str
    """
    Encodes a JSON dict to a Factorio-readable blueprint string.

    Follows the data format specification `here <https://wiki.factorio.com/Blueprint_string_format>`_.
    For the inverse operation, see :py:func:`string_to_JSON`.

    .. NOTE::

        This function does not verify the data before encoding it. Attempting
        to import an incorrectly formatted blueprint ``dict`` will usually
        result with an error in Factorio. If you need format validation,
        consider using :py:class:`draftsman.Blueprint` instead.

    :param JSON: The input JSON ``dict`` object.

    :returns: A ``str`` which can be imported into Factorio.
    """
    return "0" + base64.b64encode(
        zlib.compress(json.dumps(JSON, separators=(",", ":")).encode("utf-8"), 9)
    ).decode("utf-8")


def encode_version(major, minor, patch=0, dev_ver=0):
    # type: (int, int, int, int) -> int
    """
    Converts version components to version number.

    Encodes 4 16-bit version numbers into a 64 bit unsigned integer used
    to specify the version of a Factorio Blueprint or Blueprint Book.
    For the inverse operation, see :py:func:`decode_version`.

    :param major:   Major version number.
    :param minor:   Minor version number.
    :param patch:   Patch version number.
    :param dev_ver: Development version number, used internally by Factorio.

    :returns: A 64 bit ``int`` with all components specified.
    """
    return (major << 48) | (minor << 32) | (patch << 16) | (dev_ver)


def decode_version(version_number):
    # type: (int) -> tuple[int, int, int, int]
    """
    Converts version number to version components.
    Decodes a 64 bit unsigned integer into 4 unsigned shorts and returns them
    as a 4-length tuple, which is usually more readable than the combined
    format.
    For the inverse operation, see :py:func:`encode_version`.

    :param version_number: The version number to decode.
    :returns: a 4 length tuple in the format ``(major, minor, patch, dev_ver)``.
    """
    major = int((version_number >> 48) & 0xFFFF)
    minor = int((version_number >> 32) & 0xFFFF)
    patch = int((version_number >> 16) & 0xFFFF)
    dev_ver = int(version_number & 0xFFFF)
    return major, minor, patch, dev_ver


def version_string_to_tuple(version_string):
    # type: (str) -> tuple
    """
    Converts a version string to a tuple.

    Used extensively when parsing mod versions when updating the package's data,
    provided to the user for convinience. Splits a string by the dot character
    and converts each component to an ``int``.
    For the inverse operation, see :py:func:`version_tuple_to_string`.

    :param version_string: The version string to separate.

    :returns: A n-length tuple of the format ``(a, b, c)`` from ``"a.b.c"``
    """
    return tuple([int(elem) for elem in version_string.split(".")])


def version_tuple_to_string(version_tuple):
    # type: (tuple) -> str
    """
    Converts a version tuple to a string.

    Converts each element of the tuple to a string and then joins them with the
    '.' character.
    For the inverse operation, see, :py:func:`version_string_to_tuple`.

    :param version_tuple: The n-length tuple to interpret.

    :returns: A str of the format ``"a.b.c"`` from ``(a, b, c)``
    """
    return ".".join(str(x) for x in version_tuple)


def get_signal_type(signal_name):
    # type: (str) -> str
    """
    Returns the type of the signal based on its ID string.

    Signal ID objects in blueprints require a ``"type"`` field when specifying
    them. However, this information is redundant most of the time, as the type
    for any signal is always the same, making writing it out arduous. This
    function conveniently gets the signal type from the signal's name.

    :param signal_name: The name of the signal.
    :returns: ``"virtual"``, ``"fluid"``, or ``"item"``
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
        return six.text_type(signals.raw[signal_name])
    except KeyError:
        raise InvalidSignalError("'{}'".format(signal_name))


def signal_dict(signal_name):
    # type: (str) -> dict
    """
    Creates a Signal ID ``dict`` from the given signal name.

    Uses :py:func:`get_signal_type` to get the type for the dictionary.

    :param signal_name: The name of the signal.

    :returns: A dict with the ``"name"`` and ``type`` key's set.
    """
    return {"name": signal_name, "type": get_signal_type(signal_name)}


def dist(point1, point2):
    """
    Gets the Euclidean distance between two points.
    This is mostly just for python 2 compatability.
    """
    return math.sqrt((point1[0] - point2[0]) ** 2 + (point1[1] - point2[1]) ** 2)


def point_in_aabb(p, a):
    # type: (list, list[list, list]) -> bool
    """
    Checks to see if a point ``p`` is located inside AABB ``a``.

    :param p: A point sequence with a first and second element.
    :param a: 2-Dimensional list where the first pair is the minimum coordinate
        and the second pair is the maximum coordinate.

    :returns: True if the point is inside the box, false otherwise.
    """
    return (p[0] >= a[0][0] and p[0] <= a[1][0]) and (
        p[1] >= a[0][1] and p[1] <= a[1][1]
    )


def aabb_overlaps_aabb(a, b):
    # type: (list[list, list], list[list, list]) -> bool
    """
    Checks to see if AABB ``a`` overlaps AABB ``b``.

    :param a: 2-Dimensional list where the first pair is the minimum coordinate
        and the second pair is the maximum coordinate.
    :param b: Another AABB of the same format as ``a``.

    :returns: True if they overlap, false otherwise.
    """
    return (a[0][0] < b[1][0] and a[1][0] > b[0][0]) and (
        a[0][1] < b[1][1] and a[1][1] > b[0][1]
    )


def point_in_circle(p, r, c=(0, 0)):
    # type: (list, float, list) -> bool
    """
    Checks to see if a point ``p`` lies within radius ``r`` centered around
    point ``c``. If ``c`` is not provided, the origin is assumed.

    :param p: A point sequence with a first and second element.
    :param r: The radius of the circle.
    :param c: A point sequence with a first and second element.

    :returns: True if the point is within the circle, false otherwise.
    """
    dx = p[0] - c[0]
    dy = p[1] - c[1]
    return dx * dx + dy * dy <= r * r


def aabb_overlaps_circle(a, r, c):
    # type: (list[list, list], float, list) -> bool
    """
    Checks to see if an AABB ``a`` overlaps a circle with radius ``r`` at point
    ``c``. Algorithm pulled from https://stackoverflow.com/a/402010/8167625

    :param a: 2-Dimensional list where the first pair is the minimum coordinate
        and the second pair is the maximum coordinate.
    :param r: The radius of the circle.
    :param c: A point sequence with a first and second element. Defaults to
        origin if not specified.
    """
    aabb_width = a[1][0] - a[0][0]
    aabb_height = a[1][1] - a[0][1]
    aabb_center = (a[0][0] + aabb_width / 2, a[0][1] + aabb_height / 2)
    circle_distance = (abs(c[0] - aabb_center[0]), abs(c[1] - aabb_center[1]))

    if circle_distance[0] > (aabb_width / 2 + r):
        return False
    if circle_distance[1] > (aabb_height / 2 + r):
        return False

    if circle_distance[0] <= (aabb_width / 2):
        return True
    if circle_distance[1] <= (aabb_height / 2):
        return True

    corner_distance_sq = (circle_distance[0] - aabb_width / 2) ** 2 + (
        circle_distance[1] - aabb_height / 2
    ) ** 2

    return corner_distance_sq <= r**2


def extend_aabb(a, b):
    # type: (list[list, list], list[list, list]) -> list[list, list]
    """
    Gets the minimum AABB that encompasses two other bounding boxes. Used to
    'grow' the size of a bounding box to encompass both inputs.
    If `a` is None, then we simply return b.

    :param a: 2-Dimensional list where the first pair is the minimum coordinate
        and the second pair is the maximum coordinate.
    :param b: Another AABB of the same format as ``a``.

    :returns: The minumum bounding area between the two inputs.
    """
    if a is None:
        return b
    else:
        return [
            [min(a[0][0], b[0][0]), min(a[0][1], b[0][1])],
            [max(a[1][0], b[1][0]), max(a[1][1], b[1][1])],
        ]


def aabb_to_dimensions(aabb):
    # type: (list[list, list]) -> tuple[int, int]
    """
    Gets the tile-dimensions of an AABB, or the minimum number of tiles across
    each axis that the box would have to take up.

    :param aabb: 2-Dimensional list where the first pair is the minimum coordinate
        and the second pair is the maximum coordinate.

    :returns: a tuple of the form ``(tile_width, tile_height)``
    """
    x = int(math.ceil(aabb[1][0] - aabb[0][0]))
    y = int(math.ceil(aabb[1][1] - aabb[0][1]))
    return x, y


def get_recipe_ingredients(recipe_name):
    # type: (str) -> set[str]
    """
    Returns a set of all item types that `recipe_name` requires. Discards
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

    :returns: A ``set`` of names of each Factorio item that the recipe requires.
    """
    if "ingredients" in recipes.raw[recipe_name]:
        try:
            return {x[0] for x in recipes.raw[recipe_name]["ingredients"]}
        except KeyError:
            return {x["name"] for x in recipes.raw[recipe_name]["ingredients"]}
    else:  # "normal" in recipes.raw[recipe_name]:
        try:
            return {x[0] for x in recipes.raw[recipe_name]["normal"]["ingredients"]}
        except KeyError:
            return {
                x["name"] for x in recipes.raw[recipe_name]["normal"]["ingredients"]
            }


def reissue_warnings(func):
    # type: (Any) -> Any
    """
    Function decorator that catches all warnings issued from a function and
    re-issues them to the calling function.

    :param func: The function who's errors are caught and re-issued.

    :returns: The result of the function.
    """

    @wraps(func)
    def inner(*args, **kwargs):
        with warnings.catch_warnings(record=True) as warning_list:
            result = func(*args, **kwargs)

        for warning in warning_list:
            warnings.warn(warning.message, warning.category, stacklevel=2)

        return result

    return inner
