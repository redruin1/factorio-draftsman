# test_blueprint_book.py

from draftsman._factorio_version import __factorio_version_info__, __factorio_version__
from draftsman.classes.blueprint import Blueprint
from draftsman.classes.deconstruction_planner import DeconstructionPlanner
from draftsman.classes.upgrade_planner import UpgradePlanner
from draftsman.classes.blueprint_book import BlueprintableList, BlueprintBook
from draftsman.error import (
    InvalidSignalError,
    IncorrectBlueprintTypeError,
    DataFormatError,
)
from draftsman.signatures import Color, Icons
from draftsman.utils import encode_version, string_to_JSON
from draftsman.warning import DraftsmanWarning, UnknownSignalWarning

import pytest


class TestBlueprintableList:
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
        assert isinstance(blueprintable_list[0], Blueprint)
        assert isinstance(blueprintable_list[1], DeconstructionPlanner)
        assert isinstance(blueprintable_list[2], UpgradePlanner)
        assert isinstance(blueprintable_list[3], BlueprintBook)
        assert isinstance(blueprintable_list[4], Blueprint)
        assert isinstance(blueprintable_list[5], DeconstructionPlanner)
        assert isinstance(blueprintable_list[6], UpgradePlanner)
        assert isinstance(blueprintable_list[7], BlueprintBook)

        # Errors
        with pytest.raises(TypeError):
            BlueprintableList(["incorrect"])

        with pytest.raises(DataFormatError):
            BlueprintableList([{"incorrect": "thing"}])

    def test_setitem(self):
        blueprint_book = BlueprintBook()
        blueprint_book.blueprints.append(Blueprint())
        assert isinstance(blueprint_book.blueprints[0], Blueprint)
        blueprint_book.blueprints[0] = BlueprintBook()
        assert isinstance(blueprint_book.blueprints[0], BlueprintBook)

        with pytest.raises(TypeError):
            blueprint_book.blueprints[0] = "incorrect"

    def test_delitem(self):
        blueprint_book = BlueprintBook()
        blueprint_book.blueprints.append(Blueprint())

        del blueprint_book.blueprints[0]

        assert blueprint_book.blueprints.data == []


class TestBlueprintBook:
    def test_constructor(self):
        blueprint_book = BlueprintBook()

        assert blueprint_book.to_dict() == {
            "blueprint_book": {
                "active_index": 0,
                "item": "blueprint-book",
                "version": encode_version(*__factorio_version_info__),
            }
        }

        example = {
            "blueprint_book": {
                "active_index": 0,
                "item": "blueprint-book",
                "version": encode_version(*__factorio_version_info__),
            }
        }
        blueprint_book = BlueprintBook(example)
        assert blueprint_book.to_dict() == {
            "blueprint_book": {
                "active_index": 0,
                "item": "blueprint-book",
                "version": encode_version(*__factorio_version_info__),
            }
        }

        blueprint_book = BlueprintBook(
            "0eNqrVkrKKU0tKMrMK4lPys/PVrKqVsosSc1VskJI6IIldJQSk0syy1LjM/NSUiuUrAx0lMpSi4oz8/OUrIwsDE3MLY3MTQ1NDY3NDGprAVVBHPY="
        )
        assert blueprint_book.to_dict() == {
            "blueprint_book": {
                "active_index": 0,
                "item": "blueprint-book",
                "version": encode_version(1, 1, 53, 0),
            }
        }

        # Test icons
        blueprint_book = BlueprintBook(
            "0eNpFi1EKwjAQBe/yviPYkhjNVURK2i4SbHdLE6sScnfbIvj53sxktMOTpjlwalqRB1xGSDTC/cFhBwqhE45w14wY7uyHzU2fiVZ3TxTYj9t6ifQoa8A9veGqclPwXQoLNb/rqLDQHIMwXH2utL3U1hitjT2V8gXrTjDd"
        )
        assert blueprint_book.to_dict() == {
            "blueprint_book": {
                "active_index": 0,
                "item": "blueprint-book",
                "icons": [{"index": 1, "signal": {"name": "wood", "type": "item"}}],
                "version": encode_version(1, 1, 59, 0),
            }
        }

        # Test description
        blueprint_book = BlueprintBook(
            "0eNpNys0KgCAQBOBXiT1bVPTrrScJrT0smYaZBNG7Z14K5jLzzQVSHbhZ0m6UxizALyCHK/AP0ggMlJCoAgyJFitmYZlxnyxtjoyO+6+/LCZHHkfSM57AcwYe7R6/ZVdUbV+2dRNSdff9AJD5LO0="
        )
        # print(blueprint_book.version_tuple())
        assert blueprint_book.to_dict() == {
            "blueprint_book": {
                "active_index": 0,
                "item": "blueprint-book",
                "label": "A name.",
                "description": "A description.",
                "version": encode_version(1, 1, 61, 0),
            }
        }

        # # Incorrect constructor
        # with self.assertRaises(TypeError):
        #     BlueprintBook(TypeError)

        # # Valid blueprint string, but wrong type
        # with self.assertRaises(IncorrectBlueprintTypeError):
        #     BlueprintBook(
        #         "0eNqrVkrKKU0tKMrMK1GyqlbKLEnNVbJCEtNRKkstKs7Mz1OyMrIwNDG3NDI3NTI0s7A0q60FAHmRE1c="
        #     )

    def test_load_from_string(self):
        pass

    def test_setup(self):
        blueprint_book = BlueprintBook()
        example = {
            "label": "a label",
            "label_color": {"r": 50, "g": 50, "b": 50},
            "active_index": 0,
            "item": "blueprint-book",
            "blueprints": [],
            "version": encode_version(*__factorio_version_info__),
        }
        blueprint_book.setup(**example)
        assert blueprint_book.to_dict() == {
            "blueprint_book": {
                "label": "a label",
                "label_color": {"r": 50, "g": 50, "b": 50},
                "active_index": 0,
                "item": "blueprint-book",
                "version": encode_version(*__factorio_version_info__),
            }
        }

        with pytest.warns(DraftsmanWarning):
            blueprint_book.setup(unused_keyword="whatever")

    def test_set_label(self):
        blueprint_book = BlueprintBook()
        blueprint_book.set_version(1, 1, 54, 0)
        # String
        blueprint_book.label = "testing The LABEL"
        assert blueprint_book.label == "testing The LABEL"
        assert blueprint_book.to_dict() == {
            "blueprint_book": {
                "item": "blueprint-book",
                "label": "testing The LABEL",
                "active_index": 0,
                "version": encode_version(1, 1, 54, 0),
            }
        }
        # None
        blueprint_book.label = None
        assert blueprint_book.to_dict() == {
            "blueprint_book": {
                "item": "blueprint-book",
                "active_index": 0,
                "version": encode_version(1, 1, 54, 0),
            }
        }

    def test_set_label_color(self):
        blueprint_book = BlueprintBook()
        blueprint_book.set_version(1, 1, 54, 0)
        # Valid 3 args
        # Test for floating point conversion error by using 0.1
        blueprint_book.set_label_color(0.5, 0.1, 0.5)
        assert blueprint_book.label_color == Color(**{"r": 0.5, "g": 0.1, "b": 0.5})
        assert blueprint_book.to_dict() == {
            "blueprint_book": {
                "item": "blueprint-book",
                "label_color": {"r": 0.5, "g": 0.1, "b": 0.5},
                "active_index": 0,
                "version": encode_version(1, 1, 54, 0),
            }
        }
        # Valid 4 args
        blueprint_book.set_label_color(1.0, 1.0, 1.0, 0.25)
        assert blueprint_book.to_dict() == {
            "blueprint_book": {
                "item": "blueprint-book",
                "label_color": {"r": 1.0, "g": 1.0, "b": 1.0, "a": 0.25},
                "active_index": 0,
                "version": encode_version(1, 1, 54, 0),
            }
        }
        # Valid None
        blueprint_book.label_color = None
        assert blueprint_book.label_color == None
        assert blueprint_book.to_dict() == {
            "blueprint_book": {
                "item": "blueprint-book",
                "active_index": 0,
                "version": encode_version(1, 1, 54, 0),
            }
        }

        with pytest.raises(DataFormatError):
            blueprint_book.set_label_color(TypeError, TypeError, TypeError)

        # Invalid Data
        with pytest.raises(DataFormatError):
            blueprint_book.set_label_color("red", blueprint_book, 5)

    def test_set_icons(self):
        blueprint_book = BlueprintBook()
        # Single Icon
        blueprint_book.set_icons("signal-A")
        assert blueprint_book.icons == Icons(root=[
            {"signal": {"name": "signal-A", "type": "virtual"}, "index": 1}
        ])
        assert blueprint_book["blueprint_book"]["icons"] == Icons(root=[
            {"signal": {"name": "signal-A", "type": "virtual"}, "index": 1}
        ])
        # Multiple Icons
        blueprint_book.set_icons("signal-A", "signal-B", "signal-C")
        assert blueprint_book["blueprint_book"]["icons"] == Icons(root=[
            {"signal": {"name": "signal-A", "type": "virtual"}, "index": 1},
            {"signal": {"name": "signal-B", "type": "virtual"}, "index": 2},
            {"signal": {"name": "signal-C", "type": "virtual"}, "index": 3},
        ])

        # Raw signal dicts
        blueprint_book.icons = []
        with pytest.raises(DataFormatError):
            blueprint_book.set_icons({"name": "some-signal", "type": "some-type"})
        assert blueprint_book.icons == Icons(root=[])

        with pytest.warns(UnknownSignalWarning):
            blueprint_book.set_icons({"name": "some-signal", "type": "virtual"})
        assert blueprint_book["blueprint_book"]["icons"] == Icons(root=[
            {"signal": {"name": "some-signal", "type": "virtual"}, "index": 1}
        ])

        # None
        blueprint_book.icons = None
        assert blueprint_book.icons == None
        assert blueprint_book.to_dict() == {
            "blueprint_book": {
                "item": "blueprint-book",
                "active_index": 0,
                "version": encode_version(*__factorio_version_info__),
            }
        }

        # Incorrect Signal Name
        with pytest.raises(InvalidSignalError):
            blueprint_book.set_icons("wrong!")

        # Incorrect Signal Type
        with pytest.raises(InvalidSignalError):
            blueprint_book.set_icons(123456, "uh-oh")

    def test_set_active_index(self):
        blueprint_book = BlueprintBook()
        blueprint_book.blueprints.append(Blueprint())
        blueprint_book.blueprints.append(Blueprint())
        blueprint_book.active_index = 1
        assert blueprint_book.active_index == 1

        blueprint_book.active_index = None
        assert blueprint_book.active_index == 0

        # Warnings: TODO
        # with pytest.warns(IndexWarning):
        #     blueprint_book.active_index = 10

        # Errors
        # with pytest.raises(TypeError):
        #     blueprint_book.active_index = "incorrect"

        # with pytest.raises(IndexError):
        #     blueprint_book.active_index = -1

    def test_set_version(self):
        blueprint_book = BlueprintBook()
        blueprint_book.set_version(1, 0, 40, 0)
        assert blueprint_book.version == 281474979332096

        blueprint_book.version = None
        assert blueprint_book.version == None
        assert blueprint_book.to_dict() == {
            "blueprint_book": {"item": "blueprint-book", "active_index": 0}
        }

        with pytest.raises(TypeError):
            blueprint_book.set_version(TypeError)

        with pytest.raises(TypeError):
            blueprint_book.set_version("1", "0", "40", "0")

    def test_set_blueprints(self):
        blueprint_book = BlueprintBook()

        assert isinstance(blueprint_book.blueprints, BlueprintableList)
        assert blueprint_book.blueprints.data == []

        blueprints = [
            Blueprint({"blueprint": {"label": "A"}}),
            BlueprintBook(),
            Blueprint({"blueprint": {"label": "B"}}),
        ]

        blueprint_book.blueprints = blueprints

        assert blueprint_book.to_dict() == {
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
        }

        blueprint_book.blueprints = None
        assert isinstance(blueprint_book.blueprints, BlueprintableList)
        assert blueprint_book.blueprints.data == []

        with pytest.raises(DataFormatError):
            blueprint_book.blueprints = TypeError

    def test_version_tuple(self):
        blueprint_book = BlueprintBook()
        assert blueprint_book.version_tuple() == __factorio_version_info__
        blueprint_book.set_version(0, 0, 0, 0)
        assert blueprint_book.version_tuple() == (0, 0, 0, 0)

    def test_version_string(self):
        blueprint_book = BlueprintBook()
        assert blueprint_book.version_string() == __factorio_version__
        blueprint_book.set_version(0, 0, 0, 0)
        assert blueprint_book.version_string() == "0.0.0.0"

    def test_to_string(self):
        blueprint_book = BlueprintBook()
        blueprint_book.set_version(1, 1, 53, 0)
        # self.assertEqual(
        #     blueprint_book.to_string(),
        #     "0eNqrVkrKKU0tKMrMK4lPys/PVrKqVsosSc1VskJI6IIldJQSk0syy1LjM/NSUiuUrAx0lMpSi4oz8/OUrIwsDE3MLY3MTQ1NDY3NDGprAVVBHPY="
        # )

        # TODO: reimplement
        # assert blueprint_book.blueprints is blueprint_book._root["blueprint_book"]["blueprints"]
        # assert blueprint_book.blueprints is blueprint_book["blueprint_book"]["blueprints"]

    def test_setitem(self):
        blueprint_book = BlueprintBook()
        blueprint_book["blueprint_book"]["label"] = "whatever"
        assert blueprint_book._root["blueprint_book"]["label"] is blueprint_book.label
        assert blueprint_book["blueprint_book"]["label"] == "whatever"

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
