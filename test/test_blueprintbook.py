# test_blueprintbook.py
# -*- encoding: utf-8 -*-

from __future__ import unicode_literals

from draftsman._factorio_version import __factorio_version_info__, __factorio_version__
from draftsman.classes.blueprint import Blueprint
from draftsman.classes.deconstruction_planner import DeconstructionPlanner
from draftsman.classes.upgrade_planner import UpgradePlanner
from draftsman.classes.blueprintbook import BlueprintableList, BlueprintBook
from draftsman.error import (
    InvalidSignalError,
    IncorrectBlueprintTypeError,
    DataFormatError,
)
from draftsman.utils import encode_version, string_to_JSON
from draftsman.warning import DraftsmanWarning, IndexWarning

import sys

if sys.version_info >= (3, 3):  # pragma: no coverage
    import unittest
else:  # pragma: no coverage
    import unittest2 as unittest


class BlueprintableListTesting(unittest.TestCase):
    def test_constructor(self):
        # Test initializer conversion
        bp_string = "0eNpNjl0KgzAQhO8yz1EwmNrmKqUUfxYb0I0ksa1I7t7EQunTMsPMt7Ojm1ZanOEAvcP0lj30dYc3I7dT9sK2EDRMoBkC3M5ZrTyQG51Nt+hoCogCJnlv6CreBIiDCYa+rENsd17njlwK/Cgvawfion+QD4m9WJ9KlvPXBJKyVAIbdFGVKmbqsUH/TRZ4kvNHRZ6rurnIRqm6Vs0pxg8hIEgA"

        dp_string = "0eNqrVkpJTc7PKy4pKk0uyczPiy/ISczLSy1SsqpWKk4tKcnMSy9WssorzcnRUcosSc1VskLToAvToKNUllpUDBRRsjKyMDQxtzQyNzUDIhOL2loAsN4j2w=="

        up_string = "0eNqrViotSC9KTEmNL8hJzMtLLVKyqlYqTi0pycxLL1ayyivNydFRyixJzVWygqnUhanUUSpLLSrOzM9TsjKyMDQxtzQyNzUDIhOL2loAhpkdww=="

        bpb_string = "0eNqrVkrKKU0tKMrMK4lPys/PVrKqRogUK1lFI3FBcpklqblKVkhiOkplqUXFmfl5SlZGFoYm5pZG5qamJiam5ma1OkqZeSmpFUpWBrWxOhg6dcHW6SglJpdklqXGw5TiMa8WAEeOOPY="

        initlist = [
            Blueprint(),  # object
            DeconstructionPlanner(),  # object
            UpgradePlanner(),  # object
            BlueprintBook(),  # object
            string_to_JSON(bp_string),  # dict
            string_to_JSON(dp_string),  # dict
            string_to_JSON(up_string),  # dict
            string_to_JSON(bpb_string),  # dict
        ]

        blueprintable_list = BlueprintableList(initlist)
        self.assertIsInstance(blueprintable_list[0], Blueprint)
        self.assertIsInstance(blueprintable_list[1], DeconstructionPlanner)
        self.assertIsInstance(blueprintable_list[2], UpgradePlanner)
        self.assertIsInstance(blueprintable_list[3], BlueprintBook)
        self.assertIsInstance(blueprintable_list[4], Blueprint)
        self.assertIsInstance(blueprintable_list[5], DeconstructionPlanner)
        self.assertIsInstance(blueprintable_list[6], UpgradePlanner)
        self.assertIsInstance(blueprintable_list[7], BlueprintBook)

        # Errors
        with self.assertRaises(TypeError):
            BlueprintableList(["incorrect"])

        with self.assertRaises(TypeError):
            BlueprintableList([{"incorrect": "thing"}])

    def test_setitem(self):
        blueprint_book = BlueprintBook()
        blueprint_book.blueprints.append(Blueprint())
        self.assertIsInstance(blueprint_book.blueprints[0], Blueprint)
        blueprint_book.blueprints[0] = BlueprintBook()
        self.assertIsInstance(blueprint_book.blueprints[0], BlueprintBook)

        with self.assertRaises(TypeError):
            blueprint_book.blueprints[0] = "incorrect"

    def test_delitem(self):
        blueprint_book = BlueprintBook()
        blueprint_book.blueprints.append(Blueprint())

        del blueprint_book.blueprints[0]

        self.assertEqual(blueprint_book.blueprints.data, [])


class BlueprintBookTesting(unittest.TestCase):
    def test_constructor(self):
        blueprint_book = BlueprintBook()

        self.assertEqual(
            blueprint_book.to_dict(),
            {
                "blueprint_book": {
                    "active_index": 0,
                    "item": "blueprint-book",
                    "version": encode_version(*__factorio_version_info__),
                }
            },
        )

        example = {
            "blueprint_book": {
                "active_index": 0,
                "item": "blueprint-book",
                "version": encode_version(*__factorio_version_info__),
            }
        }
        blueprint_book = BlueprintBook(example)
        self.assertEqual(
            blueprint_book.to_dict(),
            {
                "blueprint_book": {
                    "active_index": 0,
                    "item": "blueprint-book",
                    "version": encode_version(*__factorio_version_info__),
                }
            },
        )

        blueprint_book = BlueprintBook(
            "0eNqrVkrKKU0tKMrMK4lPys/PVrKqVsosSc1VskJI6IIldJQSk0syy1LjM/NSUiuUrAx0lMpSi4oz8/OUrIwsDE3MLY3MTQ1NDY3NDGprAVVBHPY="
        )
        self.assertEqual(
            blueprint_book.to_dict(),
            {
                "blueprint_book": {
                    "active_index": 0,
                    "item": "blueprint-book",
                    "version": encode_version(1, 1, 53, 0),
                }
            },
        )

        # Test icons
        blueprint_book = BlueprintBook(
            "0eNpFi1EKwjAQBe/yviPYkhjNVURK2i4SbHdLE6sScnfbIvj53sxktMOTpjlwalqRB1xGSDTC/cFhBwqhE45w14wY7uyHzU2fiVZ3TxTYj9t6ifQoa8A9veGqclPwXQoLNb/rqLDQHIMwXH2utL3U1hitjT2V8gXrTjDd"
        )
        self.assertEqual(
            blueprint_book.to_dict(),
            {
                "blueprint_book": {
                    "active_index": 0,
                    "item": "blueprint-book",
                    "icons": [{"index": 1, "signal": {"name": "wood", "type": "item"}}],
                    "version": encode_version(1, 1, 59, 0),
                }
            },
        )

        # Test description
        blueprint_book = BlueprintBook(
            "0eNpNys0KgCAQBOBXiT1bVPTrrScJrT0smYaZBNG7Z14K5jLzzQVSHbhZ0m6UxizALyCHK/AP0ggMlJCoAgyJFitmYZlxnyxtjoyO+6+/LCZHHkfSM57AcwYe7R6/ZVdUbV+2dRNSdff9AJD5LO0="
        )
        self.assertEqual(
            blueprint_book.to_dict(),
            blueprint_book.to_dict(),
            {
                "blueprint_book": {
                    "active_index": 0,
                    "item": "blueprint-book",
                    "label": "A name.",
                    "description": "A description.",
                    "version": encode_version(1, 1, 65, 0),
                }
            },
        )

        # Incorrect constructor
        with self.assertRaises(TypeError):
            BlueprintBook(TypeError)

        # Valid blueprint string, but wrong type
        with self.assertRaises(IncorrectBlueprintTypeError):
            BlueprintBook(
                "0eNqrVkrKKU0tKMrMK1GyqlbKLEnNVbJCEtNRKkstKs7Mz1OyMrIwNDG3NDI3NTI0s7A0q60FAHmRE1c="
            )

    def test_load_from_string(self):
        pass

    def test_setup(self):
        blueprint_book = BlueprintBook()
        example = {
            "label": "a label",
            "label_color": (50, 50, 50),
            "active_index": 0,
            "item": "blueprint-book",
            "blueprints": [],
            "version": encode_version(*__factorio_version_info__),
        }
        blueprint_book.setup(**example)
        self.assertEqual(
            blueprint_book.to_dict(),
            {
                "blueprint_book": {
                    "label": "a label",
                    "label_color": {"r": 50, "g": 50, "b": 50},
                    "active_index": 0,
                    "item": "blueprint-book",
                    "version": encode_version(*__factorio_version_info__),
                }
            },
        )

        with self.assertWarns(DraftsmanWarning):
            blueprint_book.setup(unused_keyword="whatever")

    def test_set_label(self):
        blueprint_book = BlueprintBook()
        blueprint_book.version = (1, 1, 54, 0)
        # String
        blueprint_book.label = "testing The LABEL"
        self.assertEqual(blueprint_book.label, "testing The LABEL")
        self.assertEqual(
            blueprint_book.to_dict(),
            {
                "blueprint_book": {
                    "item": "blueprint-book",
                    "label": "testing The LABEL",
                    "active_index": 0,
                    "version": encode_version(1, 1, 54, 0),
                }
            },
        )
        # None
        blueprint_book.label = None
        self.assertEqual(
            blueprint_book.to_dict(),
            {
                "blueprint_book": {
                    "item": "blueprint-book",
                    "active_index": 0,
                    "version": encode_version(1, 1, 54, 0),
                }
            },
        )
        # Other
        with self.assertRaises(TypeError):
            blueprint_book.label = 100

    def test_set_label_color(self):
        blueprint_book = BlueprintBook()
        blueprint_book.version = (1, 1, 54, 0)
        # Valid 3 args
        # Test for floating point conversion error by using 0.1
        blueprint_book.label_color = (0.5, 0.1, 0.5)
        self.assertEqual(blueprint_book.label_color, {"r": 0.5, "g": 0.1, "b": 0.5})
        self.assertEqual(
            blueprint_book.to_dict(),
            {
                "blueprint_book": {
                    "item": "blueprint-book",
                    "label_color": {"r": 0.5, "g": 0.1, "b": 0.5},
                    "active_index": 0,
                    "version": encode_version(1, 1, 54, 0),
                }
            },
        )
        # Valid 4 args
        blueprint_book.label_color = (1.0, 1.0, 1.0, 0.25)
        self.assertEqual(
            blueprint_book.to_dict(),
            {
                "blueprint_book": {
                    "item": "blueprint-book",
                    "label_color": {"r": 1.0, "g": 1.0, "b": 1.0, "a": 0.25},
                    "active_index": 0,
                    "version": encode_version(1, 1, 54, 0),
                }
            },
        )
        # Valid None
        blueprint_book.label_color = None
        self.assertEqual(blueprint_book.label_color, None)
        self.assertEqual(
            blueprint_book.to_dict(),
            {
                "blueprint_book": {
                    "item": "blueprint-book",
                    "active_index": 0,
                    "version": encode_version(1, 1, 54, 0),
                }
            },
        )

        with self.assertRaises(DataFormatError):
            blueprint_book.label_color = TypeError

        # Invalid Data
        with self.assertRaises(DataFormatError):
            blueprint_book.label_color = ("red", blueprint_book, 5)

    def test_set_icons(self):
        blueprint = BlueprintBook()
        # Single Icon
        blueprint.icons = ["signal-A"]
        self.assertEqual(
            blueprint.icons,
            [{"signal": {"name": "signal-A", "type": "virtual"}, "index": 1}],
        )
        self.assertEqual(
            blueprint["icons"],
            [{"signal": {"name": "signal-A", "type": "virtual"}, "index": 1}],
        )
        # Multiple Icon
        blueprint.icons = ["signal-A", "signal-B", "signal-C"]
        self.assertEqual(
            blueprint["icons"],
            [
                {"signal": {"name": "signal-A", "type": "virtual"}, "index": 1},
                {"signal": {"name": "signal-B", "type": "virtual"}, "index": 2},
                {"signal": {"name": "signal-C", "type": "virtual"}, "index": 3},
            ],
        )
        # None
        blueprint.icons = None
        self.assertEqual(blueprint.icons, None)
        self.assertEqual(
            blueprint.to_dict(),
            {
                "blueprint_book": {
                    "item": "blueprint-book",
                    "active_index": 0,
                    "version": encode_version(*__factorio_version_info__),
                }
            },
        )

        # Incorrect Signal Name
        with self.assertRaises(DataFormatError):
            blueprint.icons = ["wrong!"]

        # Incorrect Signal Type
        with self.assertRaises(DataFormatError):
            blueprint.icons = [123456, "uh-oh"]

        # Incorrect Signal dict format
        with self.assertRaises(DataFormatError):
            blueprint.icons = [{"incorrectly": "formatted"}]

        with self.assertRaises(DataFormatError):
            blueprint.icons = TypeError

    def test_set_active_index(self):
        blueprint_book = BlueprintBook()
        blueprint_book.blueprints.append(Blueprint())
        blueprint_book.blueprints.append(Blueprint())
        blueprint_book.active_index = 1
        self.assertEqual(blueprint_book.active_index, 1)

        blueprint_book.active_index = None
        self.assertEqual(blueprint_book.active_index, 0)

        # Warnings
        with self.assertWarns(IndexWarning):
            blueprint_book.active_index = 10

        # Errors
        with self.assertRaises(TypeError):
            blueprint_book.active_index = "incorrect"

        with self.assertRaises(IndexError):
            blueprint_book.active_index = -1

    def test_set_version(self):
        blueprint_book = BlueprintBook()
        blueprint_book.version = (1, 0, 40, 0)
        self.assertEqual(blueprint_book.version, 281474979332096)

        blueprint_book.version = None
        self.assertEqual(blueprint_book.version, None)
        self.assertEqual(
            blueprint_book.to_dict(),
            {"blueprint_book": {"item": "blueprint-book", "active_index": 0}},
        )

        with self.assertRaises(TypeError):
            blueprint_book.version = TypeError

        with self.assertRaises(TypeError):
            blueprint_book.version = ("1", "0", "40", "0")

    def test_set_blueprints(self):
        blueprint_book = BlueprintBook()

        self.assertIsInstance(blueprint_book.blueprints, BlueprintableList)
        self.assertEqual(blueprint_book.blueprints.data, [])

        blueprints = [
            Blueprint({"blueprint": {"label": "A"}}),
            BlueprintBook(),
            Blueprint({"blueprint": {"label": "B"}}),
        ]

        blueprint_book.blueprints = blueprints

        self.assertEqual(
            blueprint_book.to_dict(),
            {
                "blueprint_book": {
                    "item": "blueprint-book",
                    "active_index": 0,
                    "blueprints": [
                        {
                            "index": 0,
                            "blueprint": {
                                "item": "blueprint",
                                "label": "A",
                                "version": encode_version(*__factorio_version_info__),
                            },
                        },
                        {
                            "index": 1,
                            "blueprint_book": {
                                "item": "blueprint-book",
                                "active_index": 0,
                                "version": encode_version(*__factorio_version_info__),
                            },
                        },
                        {
                            "index": 2,
                            "blueprint": {
                                "item": "blueprint",
                                "label": "B",
                                "version": encode_version(*__factorio_version_info__),
                            },
                        },
                    ],
                    "version": encode_version(*__factorio_version_info__),
                }
            },
        )

        blueprint_book.blueprints = None
        self.assertIsInstance(blueprint_book.blueprints, BlueprintableList)
        self.assertEqual(blueprint_book.blueprints.data, [])

        with self.assertRaises(TypeError):
            blueprint_book.blueprints = TypeError

    def test_version_tuple(self):
        blueprint_book = BlueprintBook()
        self.assertEqual(blueprint_book.version_tuple(), __factorio_version_info__)
        blueprint_book.version = (0, 0, 0, 0)
        self.assertEqual(blueprint_book.version_tuple(), (0, 0, 0, 0))

    def test_version_string(self):
        blueprint_book = BlueprintBook()
        self.assertEqual(blueprint_book.version_string(), __factorio_version__)
        blueprint_book.version = (0, 0, 0, 0)
        self.assertEqual(blueprint_book.version_string(), "0.0.0.0")

    def test_to_dict(self):
        pass

    def test_to_string(self):
        blueprint_book = BlueprintBook()
        blueprint_book.version = (1, 1, 53, 0)
        # self.assertEqual(
        #     blueprint_book.to_string(),
        #     "0eNqrVkrKKU0tKMrMK4lPys/PVrKqVsosSc1VskJI6IIldJQSk0syy1LjM/NSUiuUrAx0lMpSi4oz8/OUrIwsDE3MLY3MTQ1NDY3NDGprAVVBHPY="
        # )
        self.assertIs(blueprint_book.blueprints, blueprint_book._root["blueprints"])
        self.assertIs(blueprint_book.blueprints, blueprint_book["blueprints"])

    def test_setitem(self):
        blueprint_book = BlueprintBook()
        blueprint_book["label"] = "whatever"
        self.assertIs(blueprint_book._root["label"], blueprint_book.label)
        self.assertEqual(blueprint_book["label"], "whatever")

    def test_getitem(self):
        pass


#     def test_str(self):
#         blueprint_book = BlueprintBook()
#         blueprint_book.version = (1, 1, 53, 0)
#         self.assertEqual(str(blueprint_book),
#         """<BlueprintBook>{
#   "item": "blueprint-book",
#   "active_index": 0,
#   "version": 281479275151360
# }""")
