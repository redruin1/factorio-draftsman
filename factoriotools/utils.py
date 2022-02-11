# utils.py

from .errors import MalformedBlueprintString

import base64
import json
import zlib

def string_2_JSON(string: str) -> dict:
    """
    Decodes a Factorio Blueprint string to a readable JSON Dict.
    """
    try:
        return json.loads(zlib.decompress(base64.b64decode(string[1:])))
    except:
        raise MalformedBlueprintString


def JSON_2_string(JSON: dict) -> str:
    """
    Encodes a JSON dict to a Factorio-readable blueprint string.
    """
    return '0'+base64.b64encode(zlib.compress(
        json.dumps(JSON, separators=(',',':'))
        .encode('utf-8'), level=9)).decode('utf-8')


def encode_version(major: int, minor: int, 
                   patch: int = 0, dev_ver: int = 0) -> int:
    """
    Converts version components to version number.
    """
    return (major << 48) | (minor << 32) | (patch << 16) | (dev_ver)


def decode_version(number: int) -> tuple:
    """
    Converts version number to version components.
    """
    major = (number >> 48) & 0xffff
    minor = (number >> 32) & 0xffff
    patch = (number >> 16) & 0xffff
    dev_ver = number & 0xffff
    return major, minor, patch, dev_ver


def version_string_2_tuple(version_string):
    """
    Converts a version string to a tuple.
    """
    return tuple([int(elem) for elem in version_string.split('.')])


def version_tuple_2_string(version_tuple):
    """
    Converts a version tuple to a string.
    """
    return ".".join(list(version_tuple))