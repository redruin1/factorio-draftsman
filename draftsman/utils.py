# utils.py

# TODO: get rid of warn_user

from draftsman.error import MalformedBlueprintStringError, InvalidSignalError

import draftsman.data.signals as signals

import base64
import json
import math
import warnings
import zlib


# def clamp(val, min_val, max_val):
#     return max(min(val, max_val), min_val)


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


# TODO: remove
# def warn_user(message):
#     warnings.warn(message, stacklevel=3)


def dist(point1, point2):
    return math.sqrt((point1[0] - point2[0])**2 + (point1[1] - point2[1])**2)