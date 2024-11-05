# mod_settings.py

from draftsman.utils import decode_version

import os
import struct
from typing import TypedDict

ModSettings = TypedDict("ModSettings", 
    {
        "startup": dict, 
        "runtime-global": dict, 
        "runtime-per-user": dict
    }
)

def read_mod_settings(location: str) -> ModSettings:
    """
    Reads `mod_settings.dat` and stores it as an easy-to-read dict. Would be
    trivial to implement an editor with this function. (Well, assuming you write
    a function to export back to a ``.dat`` file)

    :param location: The path to the directory where 'mod-settings.dat' is 
        located.

    :returns: A dictionary with 3 keys: ``"startup"``, ``"runtime-global"``, and
        ``"runtime-per-user"``, which contain all of their respective settings.
    """
    # Property Tree Enum
    PropertyTreeType = {
        "None": 0,
        "Bool": 1,
        "Number": 2,
        "String": 3,
        "List": 4,
        "Dictionary": 5,
    }

    def get_string(binary_stream):
        string_absent = bool(
            # int.from_bytes(binary_stream.read(1), "little", signed=False)
            struct.unpack("<?", binary_stream.read(1))[0]
        )
        if string_absent:
            return None
        # handle the Space Optimized length
        length = struct.unpack("<B", binary_stream.read(1))[0]
        if length == 255:  # length is actually longer
            length = struct.unpack("<I", binary_stream.read(4))[0]
        return binary_stream.read(length).decode()

    def get_data(binary_stream):
        data_type = struct.unpack("<B", binary_stream.read(1))[0]
        binary_stream.read(1)  # any type flag, largely internal, ignore
        if data_type == PropertyTreeType["None"]:
            return None
        elif data_type == PropertyTreeType["Bool"]:
            return bool(struct.unpack("<?", binary_stream.read(1))[0])
        elif data_type == PropertyTreeType["Number"]:
            value = struct.unpack("d", binary_stream.read(8))[0]
            return value
        elif data_type == PropertyTreeType["String"]:
            return get_string(binary_stream)
        elif data_type == PropertyTreeType["List"]:
            length = struct.unpack("<I", binary_stream.read(4))
            out = list()
            for i in range(length):
                out.append(get_data(binary_stream))
            return out
        elif data_type == PropertyTreeType["Dictionary"]:
            length = struct.unpack("<I", binary_stream.read(4))[0]
            out = dict()
            for i in range(length):
                name = get_string(binary_stream)
                value = get_data(binary_stream)
                out[name] = value
            return out

    mod_settings = {}
    with open(
        os.path.join(location, "mod-settings.dat"), mode="rb"
    ) as mod_settings_dat:
        # Header
        version_num = struct.unpack("<Q", mod_settings_dat.read(8))[0]
        version = decode_version(version_num)[::-1] # Reversed, for some reason
        header_flag = bool(struct.unpack("<?", mod_settings_dat.read(1))[0])
        # It might be nice to print out the version for additional context, but
        # this doesn't seem to prohibit loading (as far as I know)
        #print(version)
        # However, we do ensure that the header flag is 0, as we are dealing 
        # with a malformed input otherwise
        assert not header_flag, "mod-settings.dat header did not end with 0 byte, malformed input"
        mod_settings = get_data(mod_settings_dat)

    return mod_settings

def write_mod_settings(mod_settings):
    """
    TODO
    """
    pass