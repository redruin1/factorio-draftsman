# test_mod_settings.py

from draftsman.environment.mod_settings import (
    PropertyTreeType,
    decode_mod_settings,
    encode_mod_settings,
    read_mod_settings,
    write_mod_settings,
)

import io
import os
import struct

# A `mod-settings.dat` written by Factorio 2.0.60
GAME_FILE = os.path.join(
    os.path.dirname(__file__),
    "..",
    ".github",
    "workflows",
    "environments",
    "issue_182",
    "mod-settings.dat",
)


class TestModSettings:
    def test_encode_reproduces_game_file(self):
        with open(GAME_FILE, "rb") as f:
            original = f.read()

        tree = decode_mod_settings(io.BytesIO(original))
        buffer = io.BytesIO()
        encode_mod_settings(buffer, tree, factorio_version=(2, 0, 60))

        assert buffer.getvalue() == original

    def test_round_trip(self):
        tree = {
            "startup": {
                "bool-setting": {"value": True},
                "string-setting": {"value": "hello мир"},
                "long-string-setting": {"value": "ж" * 200},  # 400 bytes
                "number-setting": {"value": 3.5},
                "int-setting": {"value": -42},
                "list-setting": {"value": [1, "two", None, False]},
                "nested-setting": {"value": {"inner": {"deeper": 1.0}}},
            },
            "runtime-global": {},
            "runtime-per-user": {"color-setting": {"value": {"r": 1.0}}},
        }
        buffer = io.BytesIO()
        encode_mod_settings(buffer, tree, factorio_version=(2, 0, 28))
        buffer.seek(0)

        assert decode_mod_settings(buffer) == tree

    def test_header_version(self):
        buffer = io.BytesIO()
        encode_mod_settings(buffer, {}, factorio_version=(2, 0, 28))

        # Four little-endian shorts, major first, then the empty header flag
        assert struct.unpack("<4H?", buffer.getvalue()[:9]) == (2, 0, 28, 0, False)

    def test_decode_unsigned_integer(self):
        data = (
            struct.pack("<4H?", 2, 0, 28, 0, False)
            + struct.pack("<BB", PropertyTreeType.UNSIGNED_INTEGER, 0)
            + struct.pack("<Q", 2**64 - 1)
        )

        assert decode_mod_settings(io.BytesIO(data)) == 2**64 - 1

    def test_write_and_read_file(self, tmp_path):
        tree = {
            "startup": {"some-setting": {"value": "value"}},
            "runtime-global": {},
            "runtime-per-user": {},
        }
        write_mod_settings(str(tmp_path), tree, factorio_version=(2, 0, 28))

        assert read_mod_settings(str(tmp_path)) == tree
