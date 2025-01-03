# mod_settings.py

from draftsman import __factorio_version_info__
from draftsman.utils import encode_version, decode_version

from enum import IntEnum
import io
import os
import struct
from typing import TypedDict


class PropertyTreeType(IntEnum):
    NONE = 0
    BOOL = 1
    NUMBER = 2
    STRING = 3
    LIST = 4
    DICTIONARY = 5
    SIGNED_INTEGER = 6  # Added in 2.0
    UNSIGNED_INTEGER = 7  # Added in 2.0


ModSettings = TypedDict(
    "ModSettings", {"startup": dict, "runtime-global": dict, "runtime-per-user": dict}
)


def decode_mod_settings(input_stream: io.BytesIO) -> ModSettings:
    """
    Reads a byte stream of a Factorio PropertyTree and decodes it into a JSON-
    like ``dict``. Primarily used for decoding `mod-settings.dat`.
    """
    # TODO: check endianness
    # Grab version number
    # We could return it, but it's not really useful...
    version_num = struct.unpack("<Q", input_stream.read(8))[0]
    _version = decode_version(version_num)[::-1]  # Reversed, for some reason

    # Read dummy byte (must be 0)
    header_flag = bool(struct.unpack("<?", input_stream.read(1))[0])
    assert (
        not header_flag
    ), "mod-settings.dat header did not end with 0 byte, malformed input"

    def read_string(binary_stream: io.BytesIO) -> str | None:
        string_absent = bool(struct.unpack("<?", binary_stream.read(1))[0])
        if string_absent:
            return None

        # Read a single byte of data; if it's < 255, then that's the length of
        # our string.
        length = struct.unpack("<B", binary_stream.read(1))[0]
        # If it's == 255, then that means that the string length is actually
        # encoded in the following 4 bytes:
        if length == 255:
            length = struct.unpack("<I", binary_stream.read(4))[0]

        return binary_stream.read(length).decode()

    # Read the data
    def read_node(binary_stream: io.BytesIO) -> None | bool | float | str | list | dict:
        # Read the signature byte to tell us what kind of node we're reading
        data_type = struct.unpack("<B", binary_stream.read(1))[0]
        # "Any type" flag, largely internal, ignore
        binary_stream.read(1)
        if data_type == PropertyTreeType.NONE:
            return None
        elif data_type == PropertyTreeType.BOOL:
            value = bool(struct.unpack("<?", binary_stream.read(1))[0])
            return value  # bool(struct.unpack("<?", binary_stream.read(1))[0])
        elif data_type == PropertyTreeType.NUMBER:
            value = struct.unpack("<d", binary_stream.read(8))[0]
            return value
        elif data_type == PropertyTreeType.STRING:
            return read_string(binary_stream)
        elif data_type == PropertyTreeType.LIST:
            list_length = struct.unpack("<I", binary_stream.read(4))
            out = list()
            for _ in range(list_length):
                out.append(read_node(binary_stream))
            return out
        elif data_type == PropertyTreeType.DICTIONARY:
            dict_length = struct.unpack("<I", binary_stream.read(4))[0]
            out = dict()
            for _ in range(dict_length):
                name = read_string(binary_stream)
                value = read_node(binary_stream)
                out[name] = value
            return out
        elif data_type == PropertyTreeType.SIGNED_INTEGER:
            value = struct.unpack("<q", binary_stream.read(8))[0]
            return value
        elif data_type == PropertyTreeType.UNSIGNED_INTEGER:
            value = struct.unpack("<Q", binary_stream)
        else:
            raise ValueError("Unknown PropertyTreeType ID '{}'".format(data_type))

    return read_node(input_stream)


def encode_mod_settings(
    destination: io.BytesIO,
    property_tree: dict,
    factorio_version: tuple[int] = __factorio_version_info__,
) -> None:
    """
    Writes an encoded PropertyTree from a ModSettings data object to the byte
    buffer, which can then be serialized to a `mod-settings.dat` file. This
    function is separate from the file creation step to allow for more
    flexibility, if desired.
    """
    # TODO: check endianness
    # Write version number
    version_num = encode_version(*factorio_version)
    destination.write(struct.pack("<Q"), version_num)
    # Write empty header flag
    destination.write(struct.pack("<?"), 0)

    def write_string(s: str) -> None:
        destination.write(struct.pack("<B", PropertyTreeType.STRING))
        destination.write(struct.pack("<B", 0))  # "Any type" flag, dummy value

        # Handle dynamic lengths
        if len(s) >= 255:
            destination.write(255)
            destination.write(struct.pack("<I", len(s)))
        else:
            destination.write(struct.pack("<B", len(s)))

        # Write the actual data
        destination.write(s.encode())

    def write_node(node: None | bool | float | str | list | dict) -> None:
        if node is None:
            destination.write(struct.pack("<B", PropertyTreeType.NONE))
            destination.write(struct.pack("<B", 0))  # "Any type" flag, dummy value
        elif type(node) is bool:
            destination.write(struct.pack("<B", PropertyTreeType.BOOL))
            destination.write(struct.pack("<B", 0))  # "Any type" flag, dummy value
            destination.write(struct.pack("<B", node))
        elif type(node) is float:
            destination.write(struct.pack("<B", PropertyTreeType.NUMBER))
            destination.write(struct.pack("<B", 0))  # "Any type" flag, dummy value
            destination.write(struct.pack("<d", node))
        elif type(node) is str:
            write_string(node)
        elif type(node) is list:
            destination.write(struct.pack("<B", PropertyTreeType.LIST))
            destination.write(struct.pack("<B", 0))  # "Any type" flag, dummy value
            destination.write(struct.pack("<I", len(node)))
            for elem in node:
                write_node(elem)
        elif type(dict) is dict:
            destination.write(struct.pack("<B", PropertyTreeType.DICTIONARY))
            destination.write(struct.pack("<B", 0))  # "Any type" flag, dummy value
            destination.write(struct.pack("<I", len(node)))
            for key, value in node.items():
                write_string(key)
                write_node(value)
        elif type(node) is int:
            destination.write(struct.pack("<B", PropertyTreeType.SIGNED_INTEGER))
            destination.write(struct.pack("<B", 0))  # "Any type" flag, dummy value
            destination.write(struct.pack("<q", node))

        # TODO: there might be a problem with an unsigned int getting loaded by
        # `decode_mod_settings` and getting coerced to a signed integer here;
        # but these property types are so new I will kick that can down the
        # proverbial road

    write_node(property_tree)


def read_mod_settings(mods_path: str) -> ModSettings:
    """
    Reads a `mod_settings.dat` file located at the ``mods_path`` directory.
    Returns a dict populated with the startup, per-user runtime, and global
    runtime settings organized per mod.

    :param mods_path: The path to the directory where 'mod-settings.dat' is
        located (usually next to the mods it configures).

    :returns: A dictionary with 3 keys: ``"startup"``, ``"runtime-global"``, and
        ``"runtime-per-user"``. Each entry value is dictionary of applicable
        mods, which contain all of their respective settings.
    """
    with open(
        os.path.join(mods_path, "mod-settings.dat"), mode="rb"
    ) as mod_settings_dat:
        mod_settings = decode_mod_settings(mod_settings_dat)

    return mod_settings


def write_mod_settings(mods_path: str, mod_settings: ModSettings):
    """
    Writes a `mod-settings.dat` file to a specified folder with the contents of
    ``mod_settings``. Note that no validation is done with the contents of
    ``mod_settings``, so any out-of-bounds checking is left to the user.

    :param mods_path: The path to the directory where a 'mod-settings.dat' file
        will be created or overwritten.
    :param mod_settings: A properly formatted ModSettings dictionary.
    """
    with open(
        os.path.join(mods_path, "mod-settings.dat"), mode="wb"
    ) as mod_settings_dat:
        encode_mod_settings(destination=mod_settings_dat, property_tree=mod_settings)
