# utils.py

# TODO: get rid of warn_user

from draftsman.error import MalformedBlueprintStringError, InvalidSignalError

from draftsman.data import recipes
from draftsman.data import signals

import base64
import json
import math
import warnings
import zlib


def string_2_JSON(string):
    # type: (str) -> dict
    """
    Decodes a Factorio Blueprint string to a readable JSON Dict.
    """
    try:
        return json.loads(zlib.decompress(base64.b64decode(string[1:])))
    except:
        raise MalformedBlueprintStringError


def JSON_2_string(JSON):
    # type: (dict) -> str
    """
    Encodes a JSON dict to a Factorio-readable blueprint string.
    """
    return '0'+base64.b64encode(zlib.compress(
        json.dumps(JSON, separators=(',',':'))
        .encode('utf-8'), 9)).decode('utf-8')


def encode_version(major, minor, patch = 0, dev_ver = 0):
    # type: (int, int, int, int) -> int
    """
    Converts version components to version number.
    """
    return (major << 48) | (minor << 32) | (patch << 16) | (dev_ver)


def decode_version(number):
    # type: (int) -> tuple(int, int, int, int)
    """
    Converts version number to version components.
    """
    major = int((number >> 48) & 0xffff)
    minor = int((number >> 32) & 0xffff)
    patch = int((number >> 16) & 0xffff)
    dev_ver = int(number & 0xffff)
    return major, minor, patch, dev_ver


def version_string_2_tuple(version_string):
    # type: (str) -> tuple
    """
    Converts a version string to a tuple.
    """
    return tuple([int(elem) for elem in version_string.split('.')])


def version_tuple_2_string(version_tuple):
    # type: (tuple) -> str
    """
    Converts a version tuple to a string.
    """
    #return ".".join(list(version_tuple))
    return ".".join(str(x) for x in version_tuple)


def get_signal_type(signal_name):
    # type: (str) -> str
    """
    Returns the type of the signal based on its ID string.
    """
    if signal_name in signals.virtual:
        return "virtual"
    elif signal_name in signals.fluid:
        return "fluid"
    elif signal_name in signals.item:
        return "item"
    else:
        raise InvalidSignalError("'{}'".format(str(signal_name)))

    # Or
    #return signals.raw[signal_name]["type"]


def signal_dict(name):
    # type: (str) -> dict
    return {"name": name, "type": get_signal_type(name)}


def dist(point1, point2):
    """
    Gets the Euclidean distance between two points.
    This is mostly just for python 2 compatability.
    """
    return math.sqrt((point1[0] - point2[0])**2 + (point1[1] - point2[1])**2)


def point_in_aabb(p, a):
    """
    """
    return ((p[0] >= a[0][0] and p[0] <= a[1][0]) and 
            (p[1] >= a[0][1] and p[1] <= a[1][1]))


def aabb_overlaps_aabb(a, b):
    """
    """
    return ((a[0][0] <= b[1][0] and a[1][0] >= b[0][0]) and
            (a[0][1] <= b[1][1] and a[1][1] >= b[0][1]))


def point_in_radius(p, r, c=(0,0)):
    """
    """
    dx = p[0] - c[0]
    dy = p[1] - c[1]
    return dx * dx + dy * dy <= r * r


def aabb_overlaps_circle(a, p, r):
    """
    Algorithm pulled from https://stackoverflow.com/a/402010/8167625
    """
    aabb_width = a[1][0] - a[0][0]
    aabb_height = a[1][1] - a[0][1]
    aabb_center = (a[0][0] + aabb_width / 2, a[0][1] + aabb_height / 2)
    circle_distance = (abs(p[0] - aabb_center[0]), abs(p[1] - aabb_center[1]))

    if circle_distance[0] > (aabb_width  / 2 + r): 
        return False
    if circle_distance[1] > (aabb_height / 2 + r): 
        return False
    
    if circle_distance[0] <= (aabb_width / 2): 
        return True
    if circle_distance[1] <= (aabb_height / 2): 
        return True

    corner_distance_sq = ((circle_distance[0] - aabb_width  / 2) ** 2 + 
                          (circle_distance[1] - aabb_height / 2) ** 2)

    return corner_distance_sq <= r ** 2


def extend_aabb(a, b):
    """
    Gets the minimum AABB that encompasses two other bounding boxes. Used to
    'grow' the size of a bounding box when adding entities to Group or 
    Blueprint.
    """
    return [[min(a[0][0], b[0][0]),
             min(a[0][1], b[0][1])],
            [max(a[1][0], b[1][0]),
             max(a[1][1], b[1][1])]]


def aabb_to_dimensions(aabb):
    """
    Gets the tile-dimensions of an AABB.
    """
    x = int(math.ceil(aabb[1][0] - aabb[0][0]))
    y = int(math.ceil(aabb[1][1] - aabb[0][1]))
    return x, y


def get_recipe_ingredients(recipe_name):
    """
    Returns a set of all item types that `recipe_name` requires. Discards 
    quantities.
    NOTE: Assumes that the items required for 'normal' mode are the same as
    'expensive' mode. This is unlikely true under all circumstances, but how 
    will we issue warnings for invalid item requests if we dont know what mode
    the world save is in?
    """
    try:
        return {x[0] for x in recipes.raw[recipe_name]["ingredients"]}
    except KeyError:
        return {x[0] for x in recipes.raw[recipe_name]["normal"]["ingredients"]}
    