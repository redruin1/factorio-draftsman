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
    IncompleteSignalError
)
from draftsman.signatures import AttrsColor, AttrsIcon
from draftsman.utils import encode_version, string_to_JSON
from draftsman.warning import DraftsmanWarning, IndexWarning, UnknownSignalWarning

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

        with pytest.raises(IncorrectBlueprintTypeError):
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

    def test_repr(self):
        assert repr(BlueprintBook().blueprints) == "<BlueprintableList>[]"


class TestBlueprintBook:
    def test_constructor(self):
        blueprint_book = BlueprintBook()

        assert blueprint_book.to_dict() == {
            "blueprint_book": {
                # "active_index": 0,
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
        blueprint_book = BlueprintBook.from_dict(example)
        assert blueprint_book.to_dict() == {
            "blueprint_book": {
                # "active_index": 0,
                "item": "blueprint-book",
                "version": encode_version(*__factorio_version_info__),
            }
        }

        blueprint_book = BlueprintBook.from_string(
            "0eNqrVkrKKU0tKMrMK4lPys/PVrKqVsosSc1VskJI6IIldJQSk0syy1LjM/NSUiuUrAx0lMpSi4oz8/OUrIwsDE3MLY3MTQ1NDY3NDGprAVVBHPY="
        )
        assert blueprint_book.to_dict() == {
            "blueprint_book": {
                # "active_index": 0,
                "item": "blueprint-book",
                "version": encode_version(1, 1, 53, 0),
            }
        }

        # Test icons
        blueprint_book = BlueprintBook.from_string(
            "0eNpFi1EKwjAQBe/yviPYkhjNVURK2i4SbHdLE6sScnfbIvj53sxktMOTpjlwalqRB1xGSDTC/cFhBwqhE45w14wY7uyHzU2fiVZ3TxTYj9t6ifQoa8A9veGqclPwXQoLNb/rqLDQHIMwXH2utL3U1hitjT2V8gXrTjDd"
        )
        assert blueprint_book.to_dict() == {
            "blueprint_book": {
                # "active_index": 0,
                "item": "blueprint-book",
                "icons": [{"index": 1, "signal": {"name": "wood", "type": "item"}}],
                "version": encode_version(1, 1, 59, 0),
            }
        }

        # Test description
        blueprint_book = BlueprintBook.from_string(
            "0eNpNys0KgCAQBOBXiT1bVPTrrScJrT0smYaZBNG7Z14K5jLzzQVSHbhZ0m6UxizALyCHK/AP0ggMlJCoAgyJFitmYZlxnyxtjoyO+6+/LCZHHkfSM57AcwYe7R6/ZVdUbV+2dRNSdff9AJD5LO0="
        )
        assert blueprint_book.to_dict() == {
            "blueprint_book": {
                # "active_index": 0,
                "item": "blueprint-book",
                "label": "A name.",
                "description": "A description.",
                "version": encode_version(1, 1, 61, 0),
            }
        }

        # Incorrect constructor
        # with pytest.raises(DataFormatError):
        #     BlueprintBook(DataFormatError)

        # Valid blueprint string, but wrong type
        with pytest.raises(IncorrectBlueprintTypeError):
            BlueprintBook.from_string(
                "0eNqrVkrKKU0tKMrMK1GyqlbKLEnNVbJCEtNRKkstKs7Mz1OyMrIwNDG3NDI3NTI0s7A0q60FAHmRE1c="
            )

    # def test_validate(self):
    #     incorrect_data = {
    #         "blueprint_book": {
    #             "item": "very-wrong",  # This is ignored; TODO: is this a good idea?
    #             "version": "wrong",
    #         }
    #     }
    #     bpb = BlueprintBook(incorrect_data, validate="none")
    #     assert bpb.version == "wrong"
    #     assert bpb.to_dict() == {
    #         "blueprint_book": {"item": "blueprint-book", "version": "wrong"}
    #     }

    #     # Issue Errors
    #     with pytest.raises(DataFormatError):
    #         bpb.validate().reissue_all()

    #     # Fix
    #     bpb.version = (1, 0)
    #     assert bpb.version == 281474976710656
    #     bpb.validate().reissue_all()  # Nothing

    #     bpb.validate_assignment = "none"
    #     bpb.icons = [{"signal": {"name": "unknown", "type": "item"}, "index": 0}]

    #     # No warnings
    #     bpb.validate(mode="minimum").reissue_all()

    #     # Issue warnings
    #     with pytest.warns(UnknownSignalWarning):
    #         bpb.validate(mode="strict").reissue_all()

    # def test_setup(self):
    #     blueprint_book = BlueprintBook()
    #     example = {
    #         "item": "blueprint-book",
    #         "label": "a label",
    #         "label_color": {"r": 50, "g": 50, "b": 50},
    #         "active_index": 1,
    #         "blueprints": [],
    #         "version": encode_version(*__factorio_version_info__),
    #     }
    #     blueprint_book.setup(**example)
    #     assert blueprint_book.to_dict() == {
    #         "blueprint_book": {
    #             "item": "blueprint-book",
    #             "label": "a label",
    #             "label_color": {"r": 50, "g": 50, "b": 50},
    #             "active_index": 1,
    #             "version": encode_version(*__factorio_version_info__),
    #         }
    #     }

    #     with pytest.warns(DraftsmanWarning):
    #         blueprint_book.setup(unused_keyword="whatever")  # No warning!
    #         blueprint_book.validate().reissue_all()  # Warning

    def test_set_label(self):
        blueprint_book = BlueprintBook()
        blueprint_book.version = (1, 1, 54, 0)
        # String
        blueprint_book.label = "testing The LABEL"
        assert blueprint_book.label == "testing The LABEL"
        assert blueprint_book.to_dict() == {
            "blueprint_book": {
                "item": "blueprint-book",
                "label": "testing The LABEL",
                # "active_index": 0,
                "version": encode_version(1, 1, 54, 0),
            }
        }
        # None
        blueprint_book.label = None
        assert blueprint_book.to_dict() == {
            "blueprint_book": {
                "item": "blueprint-book",
                # "active_index": 0,
                "version": encode_version(1, 1, 54, 0),
            }
        }

    def test_set_label_color(self):
        blueprint_book = BlueprintBook()
        blueprint_book.version = (1, 1, 54, 0)
        # Valid 3 args
        # Test for floating point conversion error by using 0.1
        blueprint_book.label_color = (0.5, 0.1, 0.5)
        assert blueprint_book.label_color == AttrsColor(**{"r": 0.5, "g": 0.1, "b": 0.5})
        assert blueprint_book.to_dict() == {
            "blueprint_book": {
                "item": "blueprint-book",
                "label_color": {"r": 0.5, "g": 0.1, "b": 0.5},
                # "active_index": 0,
                "version": encode_version(1, 1, 54, 0),
            }
        }
        # Valid 4 args
        blueprint_book.label_color = (1.0, 1.0, 1.0, 0.25)
        assert blueprint_book.to_dict() == {
            "blueprint_book": {
                "item": "blueprint-book",
                "label_color": {"r": 1.0, "g": 1.0, "b": 1.0, "a": 0.25},
                # "active_index": 0,
                "version": encode_version(1, 1, 54, 0),
            }
        }
        # Valid None
        blueprint_book.label_color = None
        assert blueprint_book.label_color == AttrsColor(1.0, 1.0, 1.0, 1.0)
        assert blueprint_book.to_dict() == {
            "blueprint_book": {
                "item": "blueprint-book",
                # "active_index": 0,
                "version": encode_version(1, 1, 54, 0),
            }
        }

        # TODO: reimplement
        # with pytest.raises(DataFormatError):
        #     blueprint_book.label_color = (TypeError, TypeError, TypeError)

        # # Invalid Data
        # with pytest.raises(DataFormatError):
        #     blueprint_book.label_color = ("red", blueprint_book, 5)

    def test_set_icons(self):
        blueprint_book = BlueprintBook()
        # Single Icon
        blueprint_book.set_icons("signal-A")
        assert blueprint_book.icons == [
            AttrsIcon(**{"signal": {"name": "signal-A", "type": "virtual"}, "index": 1})
        ]
        # Multiple Icons
        blueprint_book.set_icons("signal-A", "signal-B", "signal-C")
        assert blueprint_book.icons == [
            AttrsIcon(**{"signal": {"name": "signal-A", "type": "virtual"}, "index": 1}),
            AttrsIcon(**{"signal": {"name": "signal-B", "type": "virtual"}, "index": 2}),
            AttrsIcon(**{"signal": {"name": "signal-C", "type": "virtual"}, "index": 3}),
        ]

        # Raw signal dicts
        blueprint_book.icons = []
        with pytest.raises(DataFormatError):
            blueprint_book.set_icons({"name": TypeError, "type": "some-type"})
        assert blueprint_book.icons == []

        with pytest.warns(UnknownSignalWarning):
            blueprint_book.set_icons({"name": "some-signal", "type": "virtual"})
            assert blueprint_book.icons == [
                AttrsIcon(**{"signal": {"name": "some-signal", "type": "virtual"}, "index": 1})
            ]

        # None
        # blueprint_book.icons = None
        # assert blueprint_book.icons == []
        # assert blueprint_book.to_dict() == {
        #     "blueprint_book": {
        #         "item": "blueprint-book",
        #         # "active_index": 0, # Default
        #         "version": encode_version(*__factorio_version_info__),
        #     }
        # }

        # Incorrect Signal Name
        with pytest.raises(IncompleteSignalError):
            blueprint_book.set_icons("wrong!")

        # Incorrect Signal Type
        with pytest.raises(DataFormatError):
            blueprint_book.set_icons(123456, "uh-oh")

    def test_set_active_index(self):
        blueprint_book = BlueprintBook()
        blueprint_book.blueprints.append(Blueprint())
        blueprint_book.blueprints.append(Blueprint())
        blueprint_book.active_index = 1
        assert blueprint_book.active_index == 1

        # Errors
        with pytest.raises(DataFormatError):
            blueprint_book.active_index = -1
        with pytest.raises(DataFormatError):
            blueprint_book.active_index = "incorrect"

    def test_set_version(self):
        blueprint_book = BlueprintBook()
        blueprint_book.version = (1, 0, 40, 0)
        assert blueprint_book.version == 281474979332096

        with pytest.raises(DataFormatError):
            blueprint_book.version = TypeError

        with pytest.raises(DataFormatError):
            blueprint_book.version = ("1", "0", "40", "0")

    def test_set_blueprints(self):
        blueprint_book = BlueprintBook()

        assert isinstance(blueprint_book.blueprints, BlueprintableList)
        assert blueprint_book.blueprints.data == []

        blueprints = [
            Blueprint(label="A"),
            BlueprintBook(),
            Blueprint(label="B"),
        ]

        blueprint_book.blueprints = blueprints

        assert blueprint_book.to_dict() == {
            "blueprint_book": {
                "item": "blueprint-book",
                # "active_index": 0, # Default
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
                            # "active_index": 0, # Default
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

        new_blueprint_book = BlueprintBook()
        new_blueprint_book.blueprints = blueprint_book.blueprints
        assert new_blueprint_book.to_dict() == {
            "blueprint_book": {
                "item": "blueprint-book",
                # "active_index": 0, # Default
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
                            # "active_index": 0, # Default
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

        with pytest.raises(TypeError):
            blueprint_book.blueprints = TypeError

    def test_custom_index(self):
        blueprint_book = BlueprintBook()

        blueprint = Blueprint()
        blueprint_book.blueprints.append(blueprint)
        blueprint = Blueprint()
        blueprint.index = 5
        blueprint_book.blueprints.append(blueprint)

        assert blueprint_book.blueprints[1].index == 5
        assert len(blueprint_book.blueprints) == 2

        assert blueprint_book.to_dict() == {
            "blueprint_book": {
                "item": "blueprint-book",
                "blueprints": [
                    {
                        "index": 0,
                        "blueprint": {
                            "item": "blueprint",
                            "version": encode_version(*__factorio_version_info__),
                        },
                    },
                    {
                        "index": 5,
                        "blueprint": {
                            "item": "blueprint",
                            "version": encode_version(*__factorio_version_info__),
                        },
                    },
                ],
                "version": encode_version(*__factorio_version_info__),
            }
        }

        # blueprint = Blueprint(validate_assignment="none")
        # blueprint.index = "incorrect"
        # assert blueprint.index == "incorrect"
        # blueprint_book.blueprints.append(blueprint)

        # assert len(blueprint_book.blueprints) == 3
        # assert blueprint_book.to_dict() == {
        #     "blueprint_book": {
        #         "item": "blueprint-book",
        #         "blueprints": [
        #             {
        #                 # "index": 0, # Default
        #                 "blueprint": {
        #                     "item": "blueprint",
        #                     "version": encode_version(*__factorio_version_info__),
        #                 },
        #             },
        #             {
        #                 "index": 5,
        #                 "blueprint": {
        #                     "item": "blueprint",
        #                     "version": encode_version(*__factorio_version_info__),
        #                 },
        #             },
        #             {
        #                 "index": "incorrect",
        #                 "blueprint": {
        #                     "item": "blueprint",
        #                     "version": encode_version(*__factorio_version_info__),
        #                 },
        #             },
        #         ],
        #         "version": encode_version(*__factorio_version_info__),
        #     }
        # }

    def test_version_tuple(self):
        blueprint_book = BlueprintBook()
        assert blueprint_book.version_tuple() == __factorio_version_info__
        blueprint_book.version = 0
        assert blueprint_book.version_tuple() == (0, 0, 0, 0)

    def test_version_string(self):
        blueprint_book = BlueprintBook()
        assert blueprint_book.version_string() == __factorio_version__
        blueprint_book.version = (0, 0, 0, 0)
        assert blueprint_book.version_string() == "0.0.0.0"

    def test_to_string(self):
        blueprint_book = BlueprintBook()
        blueprint_book.version = (1, 1, 53, 0)
        # self.assertEqual(
        #     blueprint_book.to_string(),
        #     "0eNqrVkrKKU0tKMrMK4lPys/PVrKqVsosSc1VskJI6IIldJQSk0syy1LjM/NSUiuUrAx0lMpSi4oz8/OUrIwsDE3MLY3MTQ1NDY3NDGprAVVBHPY="
        # )

        # TODO: reimplement
        # assert blueprint_book.blueprints is blueprint_book._root["blueprint_book"]["blueprints"]
        # assert blueprint_book.blueprints is blueprint_book["blueprint_book"]["blueprints"]

    def test_import_from_string(self):
        test_string = """0eNqVj+0KgjAYhe/l/T1hqaTuViJE3YuM1jvZhwRj996KNOhH1N/Dec5HhFEHXKwi34/GXEDEt+JAnCJInAw5b8PklaF+0QMR2ofRofeK5myjoDUD5fEK4gMoNoDBitZlBUTZHuqmK5v22PGK1ymjJPEGgicWISyzHST+0PRy/lVRpfPO70+L53cGQ568Yr+t+ZKX7knXakI="""
        blueprint_book = BlueprintBook.from_string(test_string)

        assert len(blueprint_book.blueprints) == 2
        assert blueprint_book.blueprints[0].index == 0
        assert blueprint_book.blueprints[1].index == 3
        assert blueprint_book.to_dict() == {
            "blueprint_book": {
                "item": "blueprint-book",
                "version": 281479278690304,
                "blueprints": [
                    {
                        "deconstruction_planner": {
                            "item": "deconstruction-planner",
                            "version": 281479278690304,
                        },
                        "index": 0,
                    },
                    {
                        "upgrade_planner": {
                            "item": "upgrade-planner",
                            "version": 281479278690304,
                        },
                        "index": 3,
                    },
                ],
            }
        }
