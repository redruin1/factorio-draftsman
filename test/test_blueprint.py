# blueprint.py
# -*- encoding: utf-8 -*-

from __future__ import absolute_import, unicode_literals

from draftsman._factorio_version import __factorio_version__, __factorio_version_info__
from draftsman.blueprintable import Blueprint, get_blueprintable_from_string
from draftsman.classes.association import Association
from draftsman.classes.blueprint import TileList
from draftsman.classes.entitylike import EntityLike
from draftsman.classes.entitylist import EntityList
from draftsman.classes.group import Group
from draftsman.constants import Direction
from draftsman.entity import Container, ElectricPole, new_entity
from draftsman.tile import Tile
from draftsman.error import (
    MalformedBlueprintStringError,
    IncorrectBlueprintTypeError,
    InvalidConnectionSideError,
    RotationError,
    FlippingError,
    UnreasonablySizedBlueprintError,
    DraftsmanError,
    EntityNotPowerConnectableError,
    EntityNotCircuitConnectableError,
    DataFormatError,
)
from draftsman.utils import encode_version
from draftsman.warning import (
    DraftsmanWarning,
    RailAlignmentWarning,
    TooManyConnectionsWarning,
)

import sys

if sys.version_info >= (3, 3):  # pragma: no coverage
    import unittest
else:  # pragma: no coverage
    import unittest2 as unittest


class BlueprintTesting(unittest.TestCase):

    # =========================================================================
    # Blueprint
    # =========================================================================

    def test_constructor(self):
        ### Simple blueprint ###

        # Empty
        blueprint = Blueprint()
        self.assertEqual(
            blueprint.to_dict()["blueprint"],
            {
                "item": "blueprint",
                "version": encode_version(*__factorio_version_info__),
            },
        )

        # String
        blueprint = Blueprint(
            "0eNqrVkrKKU0tKMrMK1GyqlbKLEnNVbJCEtNRKkstKs7Mz1OyMrIwNDG3NDI3NTI0s7A0q60FAHmRE1c="
        )
        self.assertEqual(
            blueprint.to_dict()["blueprint"],
            {"item": "blueprint", "version": encode_version(1, 1, 54, 0)},
        )
        # self.assertEqual(
        #     blueprint.to_string(),
        #     "0eNqrVkrKKU0tKMrMK1GyqlbKLEnNVbJCEtNRKkstKs7Mz1OyMrIwNDG3NDI3NTI0s7A0q60FAHmRE1c="
        # )

        # Dict
        example = {"item": "blueprint", "version": encode_version(1, 1, 54, 0)}
        blueprint = Blueprint(example)
        self.assertEqual(blueprint.to_dict()["blueprint"], example)

        # TypeError
        with self.assertRaises(TypeError):
            Blueprint(TypeError)

        # Valid format, but blueprint book
        with self.assertRaises(IncorrectBlueprintTypeError):
            blueprint = Blueprint(
                "0eNqrVkrKKU0tKMrMK4lPys/PVrKqVsosSc1VskJI6IIldJQSk0syy1LjM/NSUiuUrAx0lMpSi4oz8/OUrIwsDE3MLY3MTSxNTcxNjWtrAVWjHQY="
            )

        # Invalid format
        with self.assertRaises(MalformedBlueprintStringError):
            blueprint = get_blueprintable_from_string("0lmaothisiswrong")

        ### Complex blueprint ###
        # TODO

    # =========================================================================

    def test_load_from_string(self):
        ### Simple blueprint ###
        blueprint = Blueprint()

        # Valid format
        blueprint.load_from_string(
            "0eNqrVkrKKU0tKMrMK1GyqlbKLEnNVbJCEtNRKkstKs7Mz1OyMrIwNDG3NDI3sTQ1MTc1rq0FAHmyE1c="
        )
        self.assertEqual(
            blueprint.to_dict()["blueprint"],
            {"item": "blueprint", "version": encode_version(1, 1, 50, 1)},
        )

        # Valid format, but blueprint book string
        with self.assertRaises(IncorrectBlueprintTypeError):
            blueprint = Blueprint(
                "0eNqrVkrKKU0tKMrMK4lPys/PVrKqVsosSc1VskJI6IIldJQSk0syy1LjM/NSUiuUrAx0lMpSi4oz8/OUrIwsDE3MLY3MTSxNTcxNjWtrAVWjHQY="
            )

        # Invalid format
        with self.assertRaises(MalformedBlueprintStringError):
            blueprint = get_blueprintable_from_string("0lmaothisiswrong")

    # =========================================================================

    def test_setup(self):
        blueprint = Blueprint()
        blueprint.setup(
            label="something",
            label_color=(1.0, 0.0, 0.0),
            icons=["signal-A", "signal-B"],
            snapping_grid_size=(32, 32),
            snapping_grid_position=(16, 16),
            position_relative_to_grid=(-5, -7),
            absolute_snapping=True,
            entities=[],
            tiles=[],
            schedules=[],
        )
        self.assertEqual(
            blueprint.to_dict()["blueprint"],
            {
                "item": "blueprint",
                "label": "something",
                "label_color": {"r": 1.0, "g": 0.0, "b": 0.0},
                "icons": [
                    {"index": 1, "signal": {"name": "signal-A", "type": "virtual"}},
                    {"index": 2, "signal": {"name": "signal-B", "type": "virtual"}},
                ],
                "snap-to-grid": {"x": 32, "y": 32},
                "position-relative-to-grid": {"x": -5, "y": -7},
                "absolute-snapping": True,
                "version": encode_version(*__factorio_version_info__),
            },
        )
        example_dict = {
            "snap-to-grid": {"x": 32, "y": 32},
            "absolute-snapping": True,
            "position-relative-to-grid": {"x": -5, "y": -7},
        }
        blueprint.setup(**example_dict)
        self.assertEqual(
            blueprint.to_dict()["blueprint"],
            {
                "item": "blueprint",
                "snap-to-grid": {"x": 32, "y": 32},
                "absolute-snapping": True,
                "position-relative-to-grid": {"x": -5, "y": -7},
                "version": encode_version(*__factorio_version_info__),
            },
        )

        with self.assertWarns(DraftsmanWarning):
            blueprint.setup(unused="whatever")

    # =========================================================================

    def test_set_label(self):
        blueprint = Blueprint()
        blueprint.version = (1, 1, 54, 0)
        # String
        blueprint.label = "testing The LABEL"
        self.assertEqual(blueprint.label, "testing The LABEL")
        self.assertEqual(
            blueprint.to_dict()["blueprint"],
            {
                "item": "blueprint",
                "label": "testing The LABEL",
                "version": encode_version(1, 1, 54, 0),
            },
        )
        # None
        blueprint.label = None
        self.assertEqual(
            blueprint.to_dict()["blueprint"],
            {"item": "blueprint", "version": encode_version(1, 1, 54, 0)},
        )
        # Other
        with self.assertRaises(TypeError):
            blueprint.label = 100

    # =========================================================================

    def test_set_label_color(self):
        blueprint = Blueprint()
        blueprint.version = (1, 1, 54, 0)
        # Valid 3 args
        # Test for floating point conversion error by using 0.1
        blueprint.label_color = (0.5, 0.1, 0.5)
        self.assertEqual(blueprint.label_color, {"r": 0.5, "g": 0.1, "b": 0.5})
        self.assertEqual(
            blueprint.to_dict()["blueprint"],
            {
                "item": "blueprint",
                "label_color": {"r": 0.5, "g": 0.1, "b": 0.5},
                "version": encode_version(1, 1, 54, 0),
            },
        )
        # Valid 4 args
        blueprint.label_color = (1.0, 1.0, 1.0, 0.25)
        self.assertEqual(
            blueprint.to_dict()["blueprint"],
            {
                "item": "blueprint",
                "label_color": {"r": 1.0, "g": 1.0, "b": 1.0, "a": 0.25},
                "version": encode_version(1, 1, 54, 0),
            },
        )
        # Valid None
        blueprint.label_color = None
        self.assertEqual(blueprint.label_color, None)
        self.assertEqual(
            blueprint.to_dict()["blueprint"],
            {"item": "blueprint", "version": encode_version(1, 1, 54, 0)},
        )
        # Invalid Data
        with self.assertRaises(DataFormatError):
            blueprint.label_color = ("red", blueprint, 5)

    # =========================================================================

    def test_set_icons(self):
        blueprint = Blueprint()
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
            blueprint.to_dict()["blueprint"],
            {
                "item": "blueprint",
                "version": encode_version(*__factorio_version_info__),
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

    # =========================================================================

    def test_set_description(self):
        blueprint = Blueprint()
        blueprint.description = "An example description."
        self.assertEqual(blueprint.description, "An example description.")
        blueprint.description = None
        self.assertEqual(blueprint.description, None)

        with self.assertRaises(TypeError):
            blueprint.description = TypeError

    # =========================================================================

    def test_set_version(self):
        blueprint = Blueprint()
        blueprint.version = (1, 0, 40, 0)
        self.assertEqual(blueprint.version, 281474979332096)

        blueprint.version = None
        self.assertEqual(blueprint.version, None)
        self.assertEqual(blueprint.to_dict()["blueprint"], {"item": "blueprint"})

        with self.assertRaises(TypeError):
            blueprint.version = TypeError

        with self.assertRaises(TypeError):
            blueprint.version = ("1", "0", "40", "0")

    # =========================================================================

    def test_set_snapping_grid_size(self):
        blueprint = Blueprint()
        blueprint.snapping_grid_size = (10, 10)
        self.assertEqual(blueprint.snapping_grid_size, {"x": 10, "y": 10})
        self.assertEqual(blueprint["snap-to-grid"], {"x": 10, "y": 10})

        blueprint.snapping_grid_size = None
        self.assertEqual(blueprint.snapping_grid_size, None)
        self.assertEqual(
            blueprint.to_dict()["blueprint"],
            {
                "item": "blueprint",
                "version": encode_version(*__factorio_version_info__),
            },
        )

        with self.assertRaises(TypeError):
            blueprint.snapping_grid_size = TypeError

    # =========================================================================

    def test_set_snapping_grid_position(self):
        blueprint = Blueprint()
        blueprint.snapping_grid_position = (1, 2)
        self.assertEqual(blueprint.snapping_grid_position, {"x": 1, "y": 2})

        with self.assertRaises(TypeError):
            blueprint.snapping_grid_position = TypeError

    # =========================================================================

    def test_set_absolute_snapping(self):
        blueprint = Blueprint()
        blueprint.absolute_snapping = True
        self.assertEqual(blueprint.absolute_snapping, True)
        self.assertEqual(blueprint["absolute-snapping"], True)

        blueprint.absolute_snapping = None
        self.assertEqual(blueprint.absolute_snapping, None)
        self.assertEqual(
            blueprint.to_dict()["blueprint"],
            {
                "item": "blueprint",
                "version": encode_version(*__factorio_version_info__),
            },
        )

        with self.assertRaises(TypeError):
            blueprint.absolute_snapping = TypeError

    # =========================================================================

    def test_set_position_relative_to_grid(self):
        blueprint = Blueprint()
        blueprint.position_relative_to_grid = (1, 2)
        self.assertEqual(blueprint.position_relative_to_grid, {"x": 1, "y": 2})
        self.assertEqual(blueprint["position-relative-to-grid"], {"x": 1, "y": 2})

        blueprint.position_relative_to_grid = None
        self.assertEqual(blueprint.position_relative_to_grid, None)
        self.assertEqual(
            blueprint.to_dict()["blueprint"],
            {
                "item": "blueprint",
                "version": encode_version(*__factorio_version_info__),
            },
        )

        with self.assertRaises(TypeError):
            blueprint.position_relative_to_grid = TypeError

    # =========================================================================

    def test_rotatable(self):
        blueprint = Blueprint()
        self.assertEqual(blueprint.rotatable, True)

    # =========================================================================

    def test_flippable(self):
        blueprint = Blueprint()

        # Test normal case
        blueprint.entities.append("transport-belt")
        self.assertEqual(blueprint.flippable, True)

        # Test unflippable case
        blueprint.entities.append("oil-refinery", tile_position=(1, 1))
        self.assertEqual(blueprint.flippable, False)

        # Test group case
        blueprint.entities = None
        group = Group("test")
        group.entities.append("pumpjack")
        blueprint.entities.append(group)
        self.assertEqual(blueprint.flippable, False)

    # =========================================================================

    def test_set_entities(self):
        blueprint = Blueprint()
        blueprint.entities = [Container()]
        self.assertIsInstance(blueprint.entities, EntityList)

        blueprint.entities = None
        self.assertIsInstance(blueprint.entities, EntityList)
        self.assertEqual(blueprint.entities.data, [])

        with self.assertRaises(TypeError):
            blueprint.entities = dict()

    # =========================================================================

    def test_set_tiles(self):
        blueprint = Blueprint()
        blueprint.tiles = [Tile("refined-concrete")]
        self.assertIsInstance(blueprint.tiles, TileList)

        blueprint.tiles = None
        self.assertIsInstance(blueprint.tiles, TileList)
        self.assertEqual(blueprint.tiles.data, [])

        with self.assertRaises(TypeError):
            blueprint.tiles = dict()

    def test_set_schedules(self):  # TODO
        blueprint = Blueprint()
        blueprint.schedules = []
        self.assertIsInstance(blueprint.schedules, list)

        blueprint.entities.append("locomotive", id="test_train")

        blueprint.schedules = [
            {
                "locomotives": [Association(blueprint.entities["test_train"])],
                "schedule": [
                    {
                        "station": "station_name",
                        "wait_conditions": [
                            {"type": "inactivity", "compare_type": "or", "ticks": 600}
                        ],
                    }
                ],
            }
        ]
        self.assertIs(blueprint.schedules[0]["locomotives"][0](), blueprint.entities[0])
        self.maxDiff = None
        self.assertEqual(
            blueprint.to_dict()["blueprint"],
            {
                "item": "blueprint",
                "entities": [
                    {
                        "name": "locomotive",
                        "position": {"x": 1.0, "y": 3.0},
                        "entity_number": 1,
                    }
                ],
                "schedules": [
                    {
                        "locomotives": [1],
                        "schedule": [
                            {
                                "station": "station_name",
                                "wait_conditions": [
                                    {
                                        "type": "inactivity",
                                        "compare_type": "or",
                                        "ticks": 600,
                                    }
                                ],
                            }
                        ],
                    }
                ],
                "version": encode_version(*__factorio_version_info__),
            },
        )

        blueprint.schedules = None
        self.assertIsInstance(blueprint.schedules, list)
        self.assertEqual(blueprint.schedules, [])

        with self.assertRaises(DataFormatError):
            blueprint.schedules = dict()

        with self.assertRaises(DataFormatError):
            blueprint.schedules = ["incorrect", "format"]

    # =========================================================================

    def test_add_entity(self):
        blueprint = Blueprint()

        # Unreasonable size
        blueprint.entities.append("inserter")
        with self.assertRaises(UnreasonablySizedBlueprintError):
            blueprint.entities.append("inserter", tile_position=(0, 100000))

    def test_change_entity_id(self):
        blueprint = Blueprint()

        blueprint.entities.append("inserter", id="old")
        self.assertIs(blueprint.entities["old"], blueprint.entities[0])
        self.assertEqual(blueprint.entities["old"].name, "inserter")

        blueprint.entities["old"] = Container("wooden-chest", id="new")
        self.assertIs(blueprint.entities["new"], blueprint.entities[0])
        with self.assertRaises(KeyError):
            blueprint.entities["old"]

    def test_move_entity(self):
        blueprint = Blueprint()

        blueprint.entities.append("wooden-chest")

        with self.assertRaises(DraftsmanError):
            blueprint.entities[0].position = (100.5, 100.5)

        with self.assertRaises(DraftsmanError):
            blueprint.entities[0].tile_position = (100, 100)

        # self.assertEqual(blueprint.area, [[100.35, 100.35], [100.65, 100.65]])
        # blueprint.entities.append("inserter")
        # with self.assertRaises(UnreasonablySizedBlueprintError):
        #     blueprint.entities[1].tile_position = (-10_000, -10_000)

    def test_move_tile(self):
        blueprint = Blueprint()

        blueprint.tiles.append("landfill")

        with self.assertRaises(DraftsmanError):
            blueprint.tiles[0].position = (100, 100)

    def test_rotate_entity(self):
        blueprint = Blueprint()
        blueprint.entities.append("inserter")
        with self.assertRaises(DraftsmanError):
            blueprint.entities[0].direction = 4

        blueprint.entities[0] = new_entity("straight-rail")
        with self.assertRaises(DraftsmanError):
            blueprint.entities[0].direction = 4

    def test_add_tile(self):
        blueprint = Blueprint()
        blueprint.version = (1, 1, 54, 0)

        # Checkerboard grid
        for x in range(2):
            for y in range(2):
                if (x + y) % 2 == 0:
                    name = "refined-concrete"
                else:
                    name = "refined-hazard-concrete-left"
                blueprint.tiles.append(name, position=(x, y))

        self.assertEqual(
            blueprint.to_dict()["blueprint"],
            {
                "item": "blueprint",
                "tiles": [
                    {"name": "refined-concrete", "position": {"x": 0, "y": 0}},
                    {
                        "name": "refined-hazard-concrete-left",
                        "position": {"x": 0, "y": 1},
                    },
                    {
                        "name": "refined-hazard-concrete-left",
                        "position": {"x": 1, "y": 0},
                    },
                    {"name": "refined-concrete", "position": {"x": 1, "y": 1}},
                ],
                "version": encode_version(1, 1, 54, 0),
            },
        )

    # =========================================================================

    def test_version_tuple(self):
        blueprint = Blueprint()
        self.assertEqual(blueprint.version_tuple(), __factorio_version_info__)
        blueprint.version = (0, 0, 0, 0)
        self.assertEqual(blueprint.version_tuple(), (0, 0, 0, 0))

    # =========================================================================

    def test_version_string(self):
        blueprint = Blueprint()
        self.assertEqual(blueprint.version_string(), __factorio_version__)
        blueprint.version = (0, 0, 0, 0)
        self.assertEqual(blueprint.version_string(), "0.0.0.0")

    # =========================================================================

    def test_recalculate_area(self):
        blueprint = Blueprint()
        blueprint.entities.append("inserter")
        blueprint.entities.append("inserter", tile_position=(1, 0))
        with self.assertRaises(UnreasonablySizedBlueprintError):
            blueprint.entities[1] = Container(tile_position=(10002, 0))

    # =========================================================================

    def test_to_dict(self):
        # List case
        blueprint = Blueprint()
        self.assertEqual(
            blueprint.to_dict()["blueprint"],
            {
                "item": "blueprint",
                "version": encode_version(*__factorio_version_info__),
            },
        )
        self.assertIs(blueprint.entities, blueprint.root["entities"])
        self.assertIs(blueprint.tiles, blueprint.root["tiles"])
        self.assertIs(blueprint.schedules, blueprint.root["schedules"])

        # Copper wire connection case
        blueprint.entities.append("power-switch", id="a")
        blueprint.entities.append("small-electric-pole", tile_position=(5, 0), id="b")
        blueprint.add_power_connection("a", "b", 1)
        blueprint.tiles.append("landfill")
        blueprint.snapping_grid_position = (-1, -1)  # also test this
        self.maxDiff = None
        self.assertEqual(
            blueprint.to_dict()["blueprint"],
            {
                "item": "blueprint",
                "entities": [
                    {
                        "name": "power-switch",
                        "position": {"x": 2.0, "y": 2.0},
                        "connections": {"Cu0": [{"entity_id": 2, "wire_id": 0}]},
                        "entity_number": 1,
                    },
                    {
                        "name": "small-electric-pole",
                        "position": {"x": 6.5, "y": 1.5},
                        "entity_number": 2,
                    },
                ],
                "tiles": [{"name": "landfill", "position": {"x": 1, "y": 1}}],
                "version": encode_version(*__factorio_version_info__),
            },
        )

        # Non-string id connection case
        example_string = "0eNqdkkFuwyAQRe8yaxwZUscp2x6jsiLbmSYjYUCA61oWdy84VRXJ3rQbxEcz/z/NsECnRrSOdAC5APVGe5DvC3i66VbltzBbBAkUcAAGuh2ysmZCV/iJQn+HyID0Fb9A8tgwQB0oED58VjFf9Dh06FLBr4MfWqUKVNgHR31hjcJkb41PvUbn4OzHq0PFYAZZnM6HKgUlQJ1aaOVcgOfD4fU5i5ISsYmpWiPd7p0ZXYYRTWQbIPFHICH+B8R3gPge0HF/xjsk5Q9HvaV4G/lmIgwmcrjeywTD4OF88aENKe6jVR7z+tZFy6d/weATnV+TxZm/1K+irnjFj6cyxm8HML+f"
        blueprint.load_from_string(example_string)
        self.maxDiff = None
        self.assertEqual(
            blueprint.to_dict()["blueprint"],
            {
                "item": "blueprint",
                "icons": [
                    {"index": 1, "signal": {"name": "power-switch", "type": "item"}}
                ],
                "entities": [
                    {
                        "name": "small-electric-pole",
                        "position": {"x": 115.5, "y": -68.5},
                        "neighbours": [2],
                        "connections": {"1": {"red": [{"entity_id": 2}]}},
                        "entity_number": 1,
                    },
                    {
                        "name": "small-electric-pole",
                        "position": {"x": 122.5, "y": -68.5},
                        "neighbours": [1],
                        "connections": {"1": {"red": [{"entity_id": 1}]}},
                        "entity_number": 2,
                    },
                    {
                        "name": "power-switch",
                        "position": {"x": 120.0, "y": -67.0},
                        "connections": {"Cu1": [{"entity_id": 2, "wire_id": 0}]},
                        "switch_state": False,
                        "entity_number": 3,
                    },
                ],
                "version": encode_version(1, 1, 53, 0),
            },
        )

        # Numeric Locomotive case
        bp_string = "0eNqN091ugjAUB/BXMee6GopWlNtd7gmWxZgKJ3IyaElb3Izh3dda4oghjnBDP86vp+HPDU51h60h5SC/ARVaWcg/b2DprGQd5ty1RciBHDbAQMkmjIykGnoGpEr8gZz37N+SWhe60Y4uOCpM+wMDVI4cYTz4PrgeVdec0Hh5qp5Bq60v0SqcFs7nWwZXyJci87Y25BUZ15NVKkJ3T276cK3zlzlXbnm/0wS9HtElGSziajqhruerYr66ma9m81UxX93PV7cPNaBqaZ1uX5HiiWS+m+HLwZvB0JZWi/fV4kOqopIGQmBsUWHZ1UNi/oIRxny0HpP82mPwLckdffDLe4fR9GIrDR6HJOuwb3h31IQEOiq+/F6+S5L+EB4W856P/igGFzQ2XmzHN9k+zQQXfL1N+v4XYYYmCA=="
        blueprint.load_from_string(bp_string)
        self.assertEqual(
            blueprint.to_dict()["blueprint"],
            {
                "icons": [
                    {"signal": {"type": "item", "name": "rail"}, "index": 1},
                    {"signal": {"type": "item", "name": "locomotive"}, "index": 2},
                ],
                "entities": [
                    {
                        "entity_number": 1,
                        "name": "locomotive",
                        "position": {"x": 116, "y": -57},
                        "orientation": 0.25,
                    },
                    {
                        "entity_number": 2,
                        "name": "straight-rail",
                        "position": {"x": 113, "y": -57},
                        "direction": 2,
                    },
                    {
                        "entity_number": 3,
                        "name": "straight-rail",
                        "position": {"x": 115, "y": -57},
                        "direction": 2,
                    },
                    {
                        "entity_number": 4,
                        "name": "straight-rail",
                        "position": {"x": 117, "y": -57},
                        "direction": 2,
                    },
                    {
                        "entity_number": 5,
                        "name": "straight-rail",
                        "position": {"x": 119, "y": -57},
                        "direction": 2,
                    },
                    {
                        "entity_number": 6,
                        "name": "train-stop",
                        "position": {"x": 119, "y": -55},
                        "direction": 2,
                        "station": "Creighton K. Yanchar",
                    },
                ],
                "schedules": [
                    {
                        "locomotives": [1],
                        "schedule": [
                            {
                                "station": "Creighton K. Yanchar",
                                "wait_conditions": [
                                    {
                                        "compare_type": "or",
                                        "type": "time",
                                        "ticks": 1800,
                                    }
                                ],
                            }
                        ],
                    }
                ],
                "item": "blueprint",
                "version": 281479275151360,
            },
        )

        # Nested List case
        blueprint = Blueprint()
        group = Group("test")
        group.entities.append(Container("wooden-chest"))
        blueprint.entities.append(group)
        blueprint.tiles.append("refined-concrete")
        self.assertEqual(
            blueprint.to_dict()["blueprint"],
            {
                "item": "blueprint",
                "entities": [
                    {
                        "name": "wooden-chest",
                        "position": {"x": 0.5, "y": 0.5},
                        "entity_number": 1,
                    }
                ],
                "tiles": [{"name": "refined-concrete", "position": {"x": 0, "y": 0}}],
                "version": encode_version(*__factorio_version_info__),
            },
        )

        # Incorrect to_dict return for custom EntityLike
        blueprint = Blueprint()

        class TestClass(EntityLike):
            @property
            def name(self):  # pragma: no coverage
                return "test"

            @property
            def type(self):  # pragma: no coverage
                return "testclass"

            @property
            def id(self):  # pragma: no coverage
                return None

            @property
            def position(self):  # pragma: no coverage
                return {"x": 0, "y": 0}

            @property
            def global_position(self):  # pragma: no coverage
                return self.position

            @property
            def collision_box(self):  # pragma: no coverage
                return [[0, 0], [1, 1]]

            @property
            def collision_mask(self):  # pragma: no coverage
                return set()

            @property
            def tile_width(self):  # pragma: no coverage
                return 1

            @property
            def tile_height(self):  # pragma: no coverage
                return 1

            def get_area(self):  # pragma: no coverage
                return [
                    [
                        self.collision_box[0][0] + self.position["x"],
                        self.collision_box[0][1] + self.position["y"],
                    ],
                    [
                        self.collision_box[1][0] + self.position["x"],
                        self.collision_box[1][1] + self.position["y"],
                    ],
                ]

            def to_dict(self):  # pragma: no coverage
                return "incorrect"

        test = TestClass()
        blueprint.entities.append(test)
        with self.assertRaises(DraftsmanError):
            blueprint.to_dict()

    # =========================================================================

    def test_getitem(self):
        blueprint = Blueprint()
        blueprint.label = "testing"
        self.assertIs(blueprint["label"], blueprint.root["label"])

    # =========================================================================

    def test_setitem(self):
        blueprint = Blueprint()
        blueprint["label"] = "testing"
        self.assertEqual(blueprint["label"], blueprint.root["label"])

    # =========================================================================

    def test_contains(self):
        blueprint = Blueprint()
        blueprint["label"] = "testing"
        self.assertEqual("label" in blueprint, True)

    # =========================================================================
    # EntityCollection
    # =========================================================================

    def test_find_entity(self):
        blueprint = Blueprint()
        blueprint.entities.append("wooden-chest", tile_position=(1, 1))
        blueprint.entities.append("iron-chest", tile_position=(5, 0))
        blueprint.entities.append("steel-chest", tile_position=(10, 10))

        found_entity = blueprint.find_entity("wooden-chest", (1.5, 1.5))
        self.assertIs(found_entity, blueprint.entities[0])

        found_entity = blueprint.find_entity("something-else", (1.5, 1.5))
        self.assertIs(found_entity, None)

        # Group search case
        group = Group("test", position=(-5, -5))
        group.entities.append("wooden-chest", tile_position=(-5, -5))
        blueprint.entities.append(group)
        # Incorrect
        found_entity = blueprint.find_entity("wooden-chest", (-4.5, -4.5))
        self.assertIs(found_entity, None)
        # Correct
        found_entity = blueprint.find_entity("wooden-chest", (-9.5, -9.5))
        self.assertIs(found_entity, blueprint.entities[("test", 0)])

    # =========================================================================

    def test_find_entities(self):
        blueprint = Blueprint()
        blueprint.entities.append("wooden-chest", tile_position=(1, 1))
        blueprint.entities.append("iron-chest", tile_position=(5, 0))
        blueprint.entities.append("steel-chest", tile_position=(10, 10))

        found_entities = blueprint.find_entities()
        self.assertEqual(found_entities, blueprint.entities.data)

        found_entities = blueprint.find_entities([[0, 0], [6, 6]])
        self.assertEqual(found_entities, [blueprint.entities[0], blueprint.entities[1]])

        # Group search case
        group = Group("test", position=(-5, -5))
        group.entities.append("wooden-chest", tile_position=(-5, -5))
        blueprint.entities.append(group)
        # Unchanged
        found_entities = blueprint.find_entities()
        self.assertEqual(found_entities, blueprint.entities.data)
        # Unchanged
        found_entities = blueprint.find_entities([[0, 0], [6, 6]])
        self.assertEqual(found_entities, [blueprint.entities[0], blueprint.entities[1]])
        # Entity group
        found_entities = blueprint.find_entities([[-10, -10], [0, 0]])
        self.assertEqual(found_entities, [blueprint.entities[("test", 0)]])

    # =========================================================================

    def test_find_entities_filtered(self):
        blueprint = Blueprint()
        blueprint.entities.append("wooden-chest", tile_position=(1, 1))
        blueprint.entities.append("decider-combinator", tile_position=(5, 0))
        blueprint.entities.append("steel-chest", tile_position=(10, 10))
        blueprint.entities.append(
            "arithmetic-combinator", tile_position=(6, 0), direction=Direction.SOUTH
        )

        self.maxDiff = None

        # Return all
        found = blueprint.find_entities_filtered()
        self.assertEqual(found, blueprint.entities.data)

        # Limit
        found = blueprint.find_entities_filtered(limit=2)
        self.assertEqual(found, [blueprint.entities[0], blueprint.entities[1]])

        # Position
        found = blueprint.find_entities_filtered(position=(1.5, 1.5))
        self.assertEqual(found, [blueprint.entities[0]])

        # Position + Radius
        found = blueprint.find_entities_filtered(position=(0, 0), radius=10)
        self.assertEqual(
            found, [blueprint.entities[0], blueprint.entities[1], blueprint.entities[3]]
        )

        # Area
        found = blueprint.find_entities_filtered(area=[[4, -1], [11, 11]])
        self.assertEqual(
            found, [blueprint.entities[1], blueprint.entities[3], blueprint.entities[2]]
        )

        # Name
        found = blueprint.find_entities_filtered(name="wooden-chest")
        self.assertEqual(found, [blueprint.entities[0]])

        # Names
        found = blueprint.find_entities_filtered(
            name={"wooden-chest", "decider-combinator"}
        )
        self.assertEqual(found, [blueprint.entities[0], blueprint.entities[1]])

        # Type
        found = blueprint.find_entities_filtered(type="container")
        self.assertEqual(found, [blueprint.entities[0], blueprint.entities[2]])

        # Types
        found = blueprint.find_entities_filtered(
            type={"container", "decider-combinator", "arithmetic-combinator"}
        )
        self.assertEqual(found, blueprint.entities.data)

        # Direction
        found = blueprint.find_entities_filtered(direction=Direction.NORTH)
        self.assertEqual(found, [blueprint.entities[1]])

        # Directions
        found = blueprint.find_entities_filtered(
            direction={Direction.NORTH, Direction.SOUTH}
        )
        self.assertEqual(found, [blueprint.entities[1], blueprint.entities[3]])

        # Invert
        found = blueprint.find_entities_filtered(
            direction={Direction.NORTH, Direction.SOUTH}, invert=True
        )
        self.assertEqual(found, [blueprint.entities[0], blueprint.entities[2]])

        # Group search case
        blueprint.entities = None
        group = Group("test")
        group.entities.append("transport-belt")
        blueprint.entities.append(group)
        found = blueprint.find_entities_filtered()
        self.assertEqual(found, [blueprint.entities[("test", 0)]])

    # =========================================================================

    def test_power_connections(self):
        blueprint = Blueprint()

        blueprint.entities.append("substation", id="1")
        blueprint.entities.append("substation", tile_position=(6, 0), id="2")

        blueprint.add_power_connection("1", "2")
        self.maxDiff = None
        self.assertEqual(
            blueprint.to_dict()["blueprint"],
            {
                "item": "blueprint",
                "entities": [
                    {
                        "name": "substation",
                        "position": {"x": 1.0, "y": 1.0},
                        "neighbours": [2],
                        "entity_number": 1,
                    },
                    {
                        "name": "substation",
                        "position": {"x": 7.0, "y": 1.0},
                        "neighbours": [1],
                        "entity_number": 2,
                    },
                ],
                "version": encode_version(*__factorio_version_info__),
            },
        )

        blueprint.remove_power_connection("2", "1")
        self.assertEqual(
            blueprint.to_dict()["blueprint"],
            {
                "item": "blueprint",
                "entities": [
                    {
                        "name": "substation",
                        "position": {"x": 1.0, "y": 1.0},
                        "entity_number": 1,
                    },
                    {
                        "name": "substation",
                        "position": {"x": 7.0, "y": 1.0},
                        "entity_number": 2,
                    },
                ],
                "version": encode_version(*__factorio_version_info__),
            },
        )

        # Errors
        blueprint.entities.append("power-switch", tile_position=(10, 10), id="p")

        with self.assertRaises(InvalidConnectionSideError):
            blueprint.add_power_connection("1", "p", 3)

        blueprint.entities.append("radar", tile_position=(0, 6), id="3")

        with self.assertRaises(EntityNotPowerConnectableError):
            blueprint.add_power_connection("3", "1")
        with self.assertRaises(EntityNotPowerConnectableError):
            blueprint.add_power_connection("1", "3")

        # Test max connections
        blueprint.entities = None
        blueprint.entities.append("substation")
        for i in range(6):
            blueprint.entities.append("substation", tile_position=((i - 3) * 2, -2))
        for i in range(5):
            blueprint.add_power_connection(0, i + 1)
        with self.assertWarns(TooManyConnectionsWarning):
            blueprint.add_power_connection(0, 6)
        with self.assertWarns(TooManyConnectionsWarning):
            blueprint.add_power_connection(6, 0)

    # =========================================================================

    def test_remove_power_connections(self):
        blueprint = Blueprint()

        blueprint.entities.append("transport-belt")
        blueprint.entities.append("small-electric-pole", tile_position=(1, 0))
        blueprint.entities.append("small-electric-pole", tile_position=(2, 0))
        blueprint.entities.append("power-switch", tile_position=(0, 1))
        blueprint.entities.append("radar", tile_position=(0, 3))

        blueprint.add_power_connection(1, 2)
        blueprint.add_power_connection(3, 1, side=1)
        blueprint.add_power_connection(3, 2, side=2)
        self.maxDiff = None
        self.assertEqual(
            blueprint.to_dict(),
            {
                "blueprint": {
                    "item": "blueprint",
                    "entities": [
                        {
                            "name": "transport-belt",
                            "position": {"x": 0.5, "y": 0.5},
                            "entity_number": 1,
                        },
                        {
                            "name": "small-electric-pole",
                            "position": {"x": 1.5, "y": 0.5},
                            "neighbours": [3],
                            "entity_number": 2,
                        },
                        {
                            "name": "small-electric-pole",
                            "position": {"x": 2.5, "y": 0.5},
                            "neighbours": [2],
                            "entity_number": 3,
                        },
                        {
                            "name": "power-switch",
                            "position": {"x": 1.0, "y": 2.0},
                            "connections": {
                                "Cu0": [{"entity_id": 2, "wire_id": 0}],
                                "Cu1": [{"entity_id": 3, "wire_id": 0}],
                            },
                            "entity_number": 4,
                        },
                        {
                            "name": "radar",
                            "position": {"x": 1.5, "y": 4.5},
                            "entity_number": 5,
                        },
                    ],
                    "version": encode_version(*__factorio_version_info__),
                }
            },
        )
        blueprint.remove_power_connections()
        self.assertEqual(
            blueprint.to_dict(),
            {
                "blueprint": {
                    "item": "blueprint",
                    "entities": [
                        {
                            "name": "transport-belt",
                            "position": {"x": 0.5, "y": 0.5},
                            "entity_number": 1,
                        },
                        {
                            "name": "small-electric-pole",
                            "position": {"x": 1.5, "y": 0.5},
                            "entity_number": 2,
                        },
                        {
                            "name": "small-electric-pole",
                            "position": {"x": 2.5, "y": 0.5},
                            "entity_number": 3,
                        },
                        {
                            "name": "power-switch",
                            "position": {"x": 1.0, "y": 2.0},
                            "entity_number": 4,
                        },
                        {
                            "name": "radar",
                            "position": {"x": 1.5, "y": 4.5},
                            "entity_number": 5,
                        },
                    ],
                    "version": encode_version(*__factorio_version_info__),
                }
            },
        )

    # =========================================================================

    def test_generate_power_connections(self):
        blueprint = Blueprint()
        self.assertEqual(
            blueprint.to_dict(),
            {
                "blueprint": {
                    "item": "blueprint",
                    "version": encode_version(*__factorio_version_info__),
                }
            },
        )
        # Null case
        blueprint.generate_power_connections()
        self.assertEqual(
            blueprint.to_dict(),
            {
                "blueprint": {
                    "item": "blueprint",
                    "version": encode_version(*__factorio_version_info__),
                }
            },
        )
        # Normal case
        pole = ElectricPole("medium-electric-pole")
        for i in range(4):
            pole.tile_position = ((i % 2) * 4, int(i / 2) * 4)
            blueprint.entities.append(pole)
        pole.tile_position = (2, 2)
        blueprint.entities.append(pole)
        self.maxDiff = None
        self.assertEqual(
            blueprint.to_dict(),
            {
                "blueprint": {
                    "item": "blueprint",
                    "entities": [
                        {
                            "name": "medium-electric-pole",
                            "position": {"x": 0.5, "y": 0.5},
                            "entity_number": 1,
                        },
                        {
                            "name": "medium-electric-pole",
                            "position": {"x": 4.5, "y": 0.5},
                            "entity_number": 2,
                        },
                        {
                            "name": "medium-electric-pole",
                            "position": {"x": 0.5, "y": 4.5},
                            "entity_number": 3,
                        },
                        {
                            "name": "medium-electric-pole",
                            "position": {"x": 4.5, "y": 4.5},
                            "entity_number": 4,
                        },
                        {
                            "name": "medium-electric-pole",
                            "position": {"x": 2.5, "y": 2.5},
                            "entity_number": 5,
                        },
                    ],
                    "version": encode_version(*__factorio_version_info__),
                }
            },
        )
        blueprint.generate_power_connections()
        self.assertEqual(
            blueprint.to_dict(),
            {
                "blueprint": {
                    "item": "blueprint",
                    "entities": [
                        {
                            "name": "medium-electric-pole",
                            "position": {"x": 0.5, "y": 0.5},
                            "neighbours": [4, 5, 3, 2],
                            "entity_number": 1,
                        },
                        {
                            "name": "medium-electric-pole",
                            "position": {"x": 4.5, "y": 0.5},
                            "neighbours": [1, 3, 5, 4],
                            "entity_number": 2,
                        },
                        {
                            "name": "medium-electric-pole",
                            "position": {"x": 0.5, "y": 4.5},
                            "neighbours": [1, 2, 5, 4],
                            "entity_number": 3,
                        },
                        {
                            "name": "medium-electric-pole",
                            "position": {"x": 4.5, "y": 4.5},
                            "neighbours": [1, 2, 3, 5],
                            "entity_number": 4,
                        },
                        {
                            "name": "medium-electric-pole",
                            "position": {"x": 2.5, "y": 2.5},
                            "neighbours": [1, 2, 3, 4],
                            "entity_number": 5,
                        },
                    ],
                    "version": encode_version(*__factorio_version_info__),
                }
            },
        )
        # Test only_axis
        blueprint.remove_power_connections()
        blueprint.generate_power_connections(only_axis=True)
        self.assertEqual(
            blueprint.to_dict(),
            {
                "blueprint": {
                    "item": "blueprint",
                    "entities": [
                        {
                            "name": "medium-electric-pole",
                            "position": {"x": 0.5, "y": 0.5},
                            "neighbours": [3, 2],
                            "entity_number": 1,
                        },
                        {
                            "name": "medium-electric-pole",
                            "position": {"x": 4.5, "y": 0.5},
                            "neighbours": [1, 4],
                            "entity_number": 2,
                        },
                        {
                            "name": "medium-electric-pole",
                            "position": {"x": 0.5, "y": 4.5},
                            "neighbours": [1, 4],
                            "entity_number": 3,
                        },
                        {
                            "name": "medium-electric-pole",
                            "position": {"x": 4.5, "y": 4.5},
                            "neighbours": [2, 3],
                            "entity_number": 4,
                        },
                        {
                            "name": "medium-electric-pole",
                            "position": {"x": 2.5, "y": 2.5},
                            "entity_number": 5,
                        },
                    ],
                    "version": encode_version(*__factorio_version_info__),
                }
            },
        )
        # Test prefer_axis
        blueprint.entities = None
        blueprint.entities.append("medium-electric-pole")
        blueprint.entities.append("medium-electric-pole", tile_position=(5, 0))
        blueprint.entities.append("medium-electric-pole", tile_position=(1, 1))
        blueprint.generate_power_connections(prefer_axis=False)
        self.assertEqual(
            blueprint.to_dict(),
            {
                "blueprint": {
                    "item": "blueprint",
                    "entities": [
                        {
                            "name": "medium-electric-pole",
                            "position": {"x": 0.5, "y": 0.5},
                            "neighbours": [2, 3],
                            "entity_number": 1,
                        },
                        {
                            "name": "medium-electric-pole",
                            "position": {"x": 5.5, "y": 0.5},
                            "neighbours": [1, 3],
                            "entity_number": 2,
                        },
                        {
                            "name": "medium-electric-pole",
                            "position": {"x": 1.5, "y": 1.5},
                            "neighbours": [1, 2],
                            "entity_number": 3,
                        },
                    ],
                    "version": encode_version(*__factorio_version_info__),
                }
            },
        )

    # =========================================================================

    def test_circuit_connections(self):
        blueprint = Blueprint()

        blueprint.entities.append("substation", id="1")
        blueprint.entities.append("substation", tile_position=(6, 0), id="2")

        blueprint.add_circuit_connection("red", "1", "2")
        self.maxDiff = None
        self.assertEqual(
            blueprint.to_dict()["blueprint"],
            {
                "item": "blueprint",
                "entities": [
                    {
                        "name": "substation",
                        "position": {"x": 1.0, "y": 1.0},
                        "connections": {"1": {"red": [{"entity_id": 2}]}},
                        "entity_number": 1,
                    },
                    {
                        "name": "substation",
                        "position": {"x": 7.0, "y": 1.0},
                        "connections": {"1": {"red": [{"entity_id": 1}]}},
                        "entity_number": 2,
                    },
                ],
                "version": encode_version(*__factorio_version_info__),
            },
        )

        blueprint.remove_circuit_connection("red", "2", "1")
        self.assertEqual(
            blueprint.to_dict()["blueprint"],
            {
                "item": "blueprint",
                "entities": [
                    {
                        "name": "substation",
                        "position": {"x": 1.0, "y": 1.0},
                        "entity_number": 1,
                    },
                    {
                        "name": "substation",
                        "position": {"x": 7.0, "y": 1.0},
                        "entity_number": 2,
                    },
                ],
                "version": encode_version(*__factorio_version_info__),
            },
        )

        # Test adjacent gate warning
        # TODO

        # Errors
        blueprint.entities.append("radar", tile_position=(0, 6), id="3")

        with self.assertRaises(EntityNotCircuitConnectableError):
            blueprint.add_circuit_connection("green", "3", "1")
        with self.assertRaises(EntityNotCircuitConnectableError):
            blueprint.add_circuit_connection("green", "1", "3")

    def test_remove_circuit_connections(self):
        blueprint = Blueprint()

        blueprint.entities.append("radar")
        blueprint.entities.append("transport-belt", tile_position=(3, 0), id="a")
        blueprint.entities.append("decider-combinator", tile_position=(4, 0), id="b")
        blueprint.entities.append("transport-belt", tile_position=(5, 0))
        blueprint.add_circuit_connection("red", "a", "b")
        blueprint.add_circuit_connection("green", "a", "b", 1, 2)
        self.maxDiff = None
        self.assertEqual(
            blueprint.to_dict(),
            {
                "blueprint": {
                    "item": "blueprint",
                    "entities": [
                        {
                            "name": "radar",
                            "position": {"x": 1.5, "y": 1.5},
                            "entity_number": 1,
                        },
                        {
                            "name": "transport-belt",
                            "position": {"x": 3.5, "y": 0.5},
                            "connections": {
                                "1": {
                                    "red": [{"entity_id": 3, "circuit_id": 1}],
                                    "green": [{"entity_id": 3, "circuit_id": 2}],
                                }
                            },
                            "entity_number": 2,
                        },
                        {
                            "name": "decider-combinator",
                            "position": {"x": 4.5, "y": 1.0},
                            "connections": {
                                "1": {"red": [{"entity_id": 2}]},
                                "2": {"green": [{"entity_id": 2}]},
                            },
                            "entity_number": 3,
                        },
                        {
                            "name": "transport-belt",
                            "position": {"x": 5.5, "y": 0.5},
                            "entity_number": 4,
                        },
                    ],
                    "version": encode_version(*__factorio_version_info__),
                }
            },
        )
        blueprint.remove_circuit_connections()
        self.assertEqual(
            blueprint.to_dict(),
            {
                "blueprint": {
                    "item": "blueprint",
                    "entities": [
                        {
                            "name": "radar",
                            "position": {"x": 1.5, "y": 1.5},
                            "entity_number": 1,
                        },
                        {
                            "name": "transport-belt",
                            "position": {"x": 3.5, "y": 0.5},
                            "entity_number": 2,
                        },
                        {
                            "name": "decider-combinator",
                            "position": {"x": 4.5, "y": 1.0},
                            "entity_number": 3,
                        },
                        {
                            "name": "transport-belt",
                            "position": {"x": 5.5, "y": 0.5},
                            "entity_number": 4,
                        },
                    ],
                    "version": encode_version(*__factorio_version_info__),
                }
            },
        )

    # =========================================================================
    # TileCollection
    # =========================================================================

    def test_find_tile(self):
        blueprint = Blueprint()
        blueprint.tiles.append("refined-concrete", position=(0, 0))
        blueprint.tiles.append("landfill", position=(10, 10))

        self.assertIs(blueprint.find_tile(0, 0), blueprint.tiles[0])
        self.assertIs(blueprint.find_tile(10, 10), blueprint.tiles[1])
        with self.assertRaises(AttributeError):
            blueprint.find_tile(5, 5).position = (15, 15)

    # =========================================================================

    def test_find_tiles_filtered(self):
        blueprint = Blueprint()
        blueprint.tiles.append("refined-concrete", position=(0, 0))
        blueprint.tiles.append("landfill", position=(10, 10))

        # No criteria
        result = blueprint.find_tiles_filtered()
        self.assertEqual(result, blueprint.tiles.data)

        # Position and radius
        result = blueprint.find_tiles_filtered(position=(0, 0), radius=5)
        self.assertEqual(result, [blueprint.tiles[0]])

        # Area
        result = blueprint.find_tiles_filtered(area=[[0, 0], [11, 11]])
        self.assertEqual(result, blueprint.tiles.data)

        # Name
        result = blueprint.find_tiles_filtered(name="refined-concrete")
        self.assertEqual(result, [blueprint.tiles[0]])

        # Names
        result = blueprint.find_tiles_filtered(name={"refined-concrete", "landfill"})
        self.assertEqual(result, blueprint.tiles.data)

        result = blueprint.find_tiles_filtered(name="refined-concrete", invert=True)
        self.assertEqual(result, [blueprint.tiles[1]])

    # =========================================================================
    # Transformable
    # =========================================================================

    def test_translate(self):
        blueprint = Blueprint()
        blueprint.entities.append("wooden-chest", tile_position=(10, 10))
        blueprint.tiles.append("refined-concrete", position=(1, 1))

        blueprint.translate(-5, -5)

        self.assertEqual(blueprint.entities[0].tile_position, {"x": 5, "y": 5})
        self.assertEqual(blueprint.tiles[0].position, {"x": -4, "y": -4})

        blueprint.entities.append("straight-rail")
        self.assertEqual(blueprint.double_grid_aligned, True)

        with self.assertWarns(RailAlignmentWarning):
            blueprint.translate(1, 1)

    # =========================================================================

    def test_rotate(self):
        blueprint = Blueprint()
        blueprint.entities.append("wooden-chest")
        blueprint.entities.append("wooden-chest", tile_position=(4, 4))
        blueprint.entities.append("boiler", tile_position=(1, 1))  # looking North

        blueprint.tiles.append("refined-concrete", position=(0, 4))
        blueprint.tiles.append("refined-concrete", position=(4, 0))

        blueprint.rotate(2)

        self.assertEqual(blueprint.entities[0].tile_position, {"x": -1, "y": 0})
        self.assertEqual(blueprint.entities[1].tile_position, {"x": -5, "y": 4})
        self.assertEqual(blueprint.entities[2].tile_position, {"x": -3, "y": 1})
        self.assertEqual(blueprint.entities[2].direction, 2)
        self.assertEqual(blueprint.tiles[0].position, {"x": -5, "y": 0})
        self.assertEqual(blueprint.tiles[1].position, {"x": -1, "y": 4})

        with self.assertRaises(RotationError):
            blueprint.rotate(1)

    # =========================================================================

    def test_flip(self):
        blueprint = Blueprint()
        blueprint.entities.append("wooden-chest")
        blueprint.entities.append("wooden-chest", tile_position=(4, 4))
        blueprint.entities.append("boiler", tile_position=(1, 1))  # looking North

        blueprint.tiles.append("refined-concrete", position=(0, 4))
        blueprint.tiles.append("refined-concrete", position=(4, 0))

        blueprint.flip()  # horizontal

        self.assertEqual(blueprint.entities[0].tile_position, {"x": -1, "y": 0})
        self.assertEqual(blueprint.entities[1].tile_position, {"x": -5, "y": 4})
        self.assertEqual(blueprint.entities[2].tile_position, {"x": -4, "y": 1})
        self.assertEqual(blueprint.entities[2].direction, 0)
        self.assertEqual(blueprint.tiles[0].position, {"x": -1, "y": 4})
        self.assertEqual(blueprint.tiles[1].position, {"x": -5, "y": 0})

        blueprint.flip("vertical")

        self.assertEqual(blueprint.entities[0].tile_position, {"x": -1, "y": -1})
        self.assertEqual(blueprint.entities[1].tile_position, {"x": -5, "y": -5})
        self.assertEqual(blueprint.entities[2].tile_position, {"x": -4, "y": -3})
        self.assertEqual(blueprint.entities[2].direction, 4)
        self.assertEqual(blueprint.tiles[0].position, {"x": -1, "y": -5})
        self.assertEqual(blueprint.tiles[1].position, {"x": -5, "y": -1})

        with self.assertRaises(ValueError):
            blueprint.flip("incorrectly")
        with self.assertRaises(FlippingError):
            blueprint.entities.append("chemical-plant", tile_position=(4, 4))
            blueprint.flip()
