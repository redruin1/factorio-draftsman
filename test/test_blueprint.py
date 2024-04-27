# blueprint.py

from draftsman._factorio_version import __factorio_version__, __factorio_version_info__
from draftsman.blueprintable import Blueprint, get_blueprintable_from_string
from draftsman.classes.association import Association
from draftsman.classes.blueprint import TileList
from draftsman.classes.collision_set import CollisionSet
from draftsman.classes.entity_like import EntityLike
from draftsman.classes.entity_list import EntityList
from draftsman.classes.group import Group
from draftsman.classes.schedule import Schedule, WaitCondition
from draftsman.classes.schedule_list import ScheduleList
from draftsman.classes.train_configuration import TrainConfiguration
from draftsman.classes.vector import Vector
from draftsman.constants import (
    Direction,
    Orientation,
    WaitConditionType,
    ValidationMode,
)
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
    InvalidAssociationError,
    InvalidSignalError,
    InvalidEntityError,
    InvalidTileError,
)
from draftsman.signatures import Color, Icon
from draftsman.utils import encode_version, AABB
from draftsman.warning import (
    DraftsmanWarning,
    GridAlignmentWarning,
    TooManyConnectionsWarning,
    UnknownEntityWarning,
    UnknownTileWarning,
)

import pytest


class TestBlueprint:

    # =========================================================================
    # Blueprint
    # =========================================================================

    # deal_test_constructor = deal.cases(Blueprint, count=50)
    def test_constructor(self):
        ### Simple blueprint ###

        # Empty
        blueprint = Blueprint()
        assert blueprint.to_dict()["blueprint"] == {
            "item": "blueprint",
            "version": encode_version(*__factorio_version_info__),
        }

        # String
        blueprint = Blueprint(
            "0eNqrVkrKKU0tKMrMK1GyqlbKLEnNVbJCEtNRKkstKs7Mz1OyMrIwNDG3NDI3NTI0s7A0q60FAHmRE1c="
        )
        # self.assertEqual(
        #     blueprint.to_dict()["blueprint"],
        #     {"item": "blueprint", "version": encode_version(1, 1, 54, 0)},
        # )
        assert blueprint.to_dict()["blueprint"] == {
            "item": "blueprint",
            "version": encode_version(1, 1, 54, 0),
        }
        # This doesn't work on Python 2 (I believe) because the order is not guaranteed
        # self.assertEqual(
        #     blueprint.to_string(),
        #     "0eNqrVkrKKU0tKMrMK1GyqlbKLEnNVbJCEtNRKkstKs7Mz1OyMrIwNDG3NDI3NTI0s7A0q60FAHmRE1c="
        # )

        # Dict
        example = {
            "blueprint": {"item": "blueprint", "version": encode_version(1, 1, 54, 0)}
        }
        blueprint = Blueprint(example)
        assert blueprint.to_dict() == example

        blueprint = Blueprint(example, validate="none")
        assert blueprint.to_dict() == example

        broken_example = {"blueprint": {"item": "blueprint", "version": "incorrect"}}

        with pytest.raises(DataFormatError):
            Blueprint(broken_example)

        blueprint = Blueprint(broken_example, validate="none")
        assert blueprint.to_dict() == broken_example

        # # TypeError
        # with self.assertRaises(TypeError):
        #     Blueprint(TypeError)

        # # Valid format, but incorrect type
        # with self.assertRaises(IncorrectBlueprintTypeError):
        #     blueprint = Blueprint(
        #         "0eNqrVkrKKU0tKMrMK4lPys/PVrKqVsosSc1VskJI6IIldJQSk0syy1LjM/NSUiuUrAx0lMpSi4oz8/OUrIwsDE3MLY3MTSxNTcxNjWtrAVWjHQY="
        #     )

        # # Invalid format
        # with self.assertRaises(MalformedBlueprintStringError):
        #     blueprint = get_blueprintable_from_string("0lmaothisiswrong")

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
        assert blueprint.to_dict()["blueprint"] == {
            "item": "blueprint",
            "version": encode_version(1, 1, 50, 1),
        }

        # # Valid format, but blueprint book string
        # with self.assertRaises(IncorrectBlueprintTypeError):
        #     blueprint = Blueprint(
        #         "0eNqrVkrKKU0tKMrMK4lPys/PVrKqVsosSc1VskJI6IIldJQSk0syy1LjM/NSUiuUrAx0lMpSi4oz8/OUrIwsDE3MLY3MTSxNTcxNjWtrAVWjHQY="
        #     )

        # # Invalid format
        # with self.assertRaises(MalformedBlueprintStringError):
        #     blueprint = get_blueprintable_from_string("0lmaothisiswrong")

    # =========================================================================

    def test_setup(self):
        blueprint = Blueprint()
        blueprint.setup(
            label="something",
            label_color={"r": 1.0, "g": 0.0, "b": 0.0},
            icons=[
                {"index": 1, "signal": {"name": "signal-A", "type": "virtual"}},
                {"index": 2, "signal": {"name": "signal-B", "type": "virtual"}},
            ],
            snapping_grid_size=(32, 32),
            snapping_grid_position=(16, 16),
            position_relative_to_grid=(-5, -7),
            absolute_snapping=True,
            entities=[],
            tiles=[],
            schedules=[],
        )
        assert blueprint.to_dict()["blueprint"] == {
            "item": "blueprint",
            "label": "something",
            "label_color": {"r": 1.0, "g": 0.0, "b": 0.0},
            "icons": [
                {"index": 1, "signal": {"name": "signal-A", "type": "virtual"}},
                {"index": 2, "signal": {"name": "signal-B", "type": "virtual"}},
            ],
            "snap-to-grid": {"x": 32, "y": 32},
            "position-relative-to-grid": {"x": -5, "y": -7},
            # "absolute-snapping": True, # Default
            "version": encode_version(*__factorio_version_info__),
        }
        example_dict = {
            "snap-to-grid": {"x": 32, "y": 32},
            "absolute-snapping": True,
            "position-relative-to-grid": {"x": -5, "y": -7},
        }
        blueprint.setup(**example_dict)
        assert blueprint.to_dict()["blueprint"] == {
            "item": "blueprint",
            "snap-to-grid": {"x": 32, "y": 32},
            # "absolute-snapping": True, # Default
            "position-relative-to-grid": {"x": -5, "y": -7},
            "version": encode_version(*__factorio_version_info__),
        }

        with pytest.warns(DraftsmanWarning):
            blueprint.setup(unused="whatever")
            blueprint.validate().reissue_all()

    # =========================================================================

    def test_set_label(self):
        blueprint = Blueprint()
        blueprint.set_version(1, 1, 54, 0)
        # String
        blueprint.label = "testing The LABEL"
        assert blueprint.label == "testing The LABEL"
        assert blueprint.to_dict()["blueprint"] == {
            "item": "blueprint",
            "label": "testing The LABEL",
            "version": encode_version(1, 1, 54, 0),
        }
        # None
        blueprint.label = None
        assert blueprint.to_dict()["blueprint"] == {
            "item": "blueprint",
            "version": encode_version(1, 1, 54, 0),
        }

    # =========================================================================

    def test_set_label_color(self):
        blueprint = Blueprint()
        blueprint.set_version(1, 1, 54, 0)
        # Valid 3 args
        # Test for floating point conversion error by using 0.1
        blueprint.set_label_color(0.5, 0.1, 0.5)
        assert blueprint.label_color == Color(**{"r": 0.5, "g": 0.1, "b": 0.5})
        assert blueprint.to_dict()["blueprint"] == {
            "item": "blueprint",
            "label_color": {"r": 0.5, "g": 0.1, "b": 0.5},
            "version": encode_version(1, 1, 54, 0),
        }
        # Valid 4 args
        blueprint.set_label_color(1.0, 1.0, 1.0, 0.25)
        assert blueprint.to_dict()["blueprint"] == {
            "item": "blueprint",
            "label_color": {"r": 1.0, "g": 1.0, "b": 1.0, "a": 0.25},
            "version": encode_version(1, 1, 54, 0),
        }
        # Valid None
        blueprint.label_color = None
        assert blueprint.label_color == None
        assert blueprint.to_dict()["blueprint"] == {
            "item": "blueprint",
            "version": encode_version(1, 1, 54, 0),
        }
        # Invalid Data
        with pytest.raises(DataFormatError):
            blueprint.set_label_color("red", blueprint, 5)

    # =========================================================================

    def test_set_icons(self):
        blueprint = Blueprint()
        # Single Icon
        blueprint.set_icons("signal-A")
        assert blueprint.icons == [
            Icon(**{"signal": {"name": "signal-A", "type": "virtual"}, "index": 1})
        ]
        assert blueprint["blueprint"]["icons"] == [
            Icon(**{"signal": {"name": "signal-A", "type": "virtual"}, "index": 1})
        ]
        # Multiple Icon
        blueprint.set_icons("signal-A", "signal-B", "signal-C")
        assert blueprint["blueprint"]["icons"] == [
            Icon(**{"signal": {"name": "signal-A", "type": "virtual"}, "index": 1}),
            Icon(**{"signal": {"name": "signal-B", "type": "virtual"}, "index": 2}),
            Icon(**{"signal": {"name": "signal-C", "type": "virtual"}, "index": 3}),
        ]

        # Raw signal dicts:
        # TODO: reimplement
        # blueprint.set_icons({"name": "some-signal", "type": "some-type"})
        # assert blueprint["blueprint"]["icons"] == [
        #     {"signal": {"name": "some-signal", "type": "some-type"}, "index": 1}
        # ]

        # None
        blueprint.icons = None
        assert blueprint.icons == None
        assert blueprint.to_dict()["blueprint"] == {
            "item": "blueprint",
            "version": encode_version(*__factorio_version_info__),
        }

        # Incorrect Signal Name
        with pytest.raises(InvalidSignalError):
            blueprint.set_icons("wrong!")

        # Incorrect Signal Type
        with pytest.raises(InvalidSignalError):
            blueprint.set_icons(123456, "uh-oh")

        # Incorrect Signal dict format
        # with pytest.raises(TypeError):
        #     blueprint.set_icons({"incorrectly": "formatted"})

        with pytest.raises(DataFormatError):
            blueprint.icons = "incorrect"

        blueprint.validate_assignment = "none"
        assert blueprint.validate_assignment == ValidationMode.NONE

        blueprint.icons = "incorrect"
        assert blueprint.icons == "incorrect"
        assert blueprint.to_dict() == {
            "blueprint": {
                "item": "blueprint",
                "version": encode_version(*__factorio_version_info__),
                "icons": "incorrect",
            }
        }

    # =========================================================================

    def test_set_description(self):
        blueprint = Blueprint()
        blueprint.description = "An example description."
        assert blueprint.description == "An example description."
        blueprint.description = None
        assert blueprint.description == None

    # =========================================================================

    def test_set_version(self):
        blueprint = Blueprint()
        blueprint.set_version(1, 0, 40, 0)
        assert blueprint.version == 281474979332096

        blueprint.version = None
        assert blueprint.version == None
        assert blueprint.to_dict()["blueprint"] == {"item": "blueprint"}

        with pytest.raises(TypeError):
            blueprint.set_version(TypeError, TypeError)

        with pytest.raises(TypeError):
            blueprint.set_version("1", "0", "40", "0")

    # =========================================================================

    def test_set_snapping_grid_size(self):
        blueprint = Blueprint()
        blueprint.snapping_grid_size = (10, 10)
        assert blueprint.snapping_grid_size == Vector(10, 10)
        # assert blueprint["blueprint"]["snap-to-grid"] == Vector(10, 10) # TODO

        blueprint.snapping_grid_size = None
        assert blueprint.snapping_grid_size == Vector(0, 0)
        assert blueprint.to_dict()["blueprint"] == {
            "item": "blueprint",
            "version": encode_version(*__factorio_version_info__),
        }

        with pytest.raises(TypeError):
            blueprint.snapping_grid_size = TypeError

    # =========================================================================

    def test_set_snapping_grid_position(self):
        blueprint = Blueprint()
        blueprint.snapping_grid_position = (1, 2)
        assert blueprint.snapping_grid_position == Vector(1, 2)

        with pytest.raises(TypeError):
            blueprint.snapping_grid_position = TypeError

    # =========================================================================

    def test_set_absolute_snapping(self):
        blueprint = Blueprint()
        blueprint.absolute_snapping = True
        assert blueprint.absolute_snapping == True
        assert blueprint["blueprint"]["absolute-snapping"] == True

        blueprint.absolute_snapping = None
        assert blueprint.absolute_snapping == None
        assert blueprint.to_dict()["blueprint"] == {
            "item": "blueprint",
            "version": encode_version(*__factorio_version_info__),
        }

        with pytest.raises(DataFormatError):
            blueprint.absolute_snapping = TypeError

    # =========================================================================

    def test_set_position_relative_to_grid(self):
        blueprint = Blueprint()
        blueprint.position_relative_to_grid = (1, 2)
        assert blueprint.position_relative_to_grid == Vector(1, 2)
        # assert blueprint["blueprint"]["position-relative-to-grid"] == Vector(1, 2) # TODO

        blueprint.position_relative_to_grid = None
        assert blueprint.position_relative_to_grid == Vector(0, 0)
        assert blueprint.to_dict()["blueprint"] == {
            "item": "blueprint",
            "version": encode_version(*__factorio_version_info__),
        }

        with pytest.raises(TypeError):
            blueprint.position_relative_to_grid = TypeError

    # =========================================================================

    def test_rotatable(self):
        blueprint = Blueprint()
        assert blueprint.rotatable == True

    # =========================================================================

    def test_flippable(self):
        blueprint = Blueprint()

        # Test normal case
        blueprint.entities.append("transport-belt")
        assert blueprint.flippable == True

        # Test unflippable case
        blueprint.entities.append("oil-refinery", tile_position=(1, 1))
        assert blueprint.flippable == False

        # Test group case
        blueprint.entities = None
        group = Group("test")
        group.entities.append("pumpjack")
        blueprint.entities.append(group)
        assert blueprint.flippable == False

    # =========================================================================

    def test_set_entities(self):
        blueprint = Blueprint()
        blueprint.entities = [Container()]
        assert isinstance(blueprint.entities, EntityList)

        blueprint.entities = None
        assert isinstance(blueprint.entities, EntityList)
        assert blueprint.entities._root == []

        # set by EntityList
        blueprint.entities.append("wooden-chest")
        blueprint.entities.append("wooden-chest", tile_position=(1, 0))
        blueprint.add_circuit_connection("red", 0, 1)
        blueprint2 = Blueprint()
        blueprint2.entities = blueprint.entities
        assert isinstance(blueprint.entities, EntityList)
        assert isinstance(blueprint2.entities, EntityList)
        # Ensure blueprint1 is still correct

        with pytest.raises(TypeError):
            blueprint.entities = dict()

    # =========================================================================

    def test_set_tiles(self):
        blueprint = Blueprint()
        blueprint.tiles = [Tile("refined-concrete")]
        assert isinstance(blueprint.tiles, TileList)

        blueprint.tiles = None
        assert isinstance(blueprint.tiles, TileList)
        assert blueprint.tiles._root == []

        blueprint.tiles.append("landfill")
        blueprint2 = Blueprint()
        blueprint2.tiles = blueprint.tiles
        assert isinstance(blueprint.tiles, TileList)
        assert isinstance(blueprint2.tiles, TileList)
        assert blueprint.tiles[0].parent is blueprint
        assert blueprint2.tiles[0].parent is not blueprint

        with pytest.raises(TypeError):
            blueprint.tiles = dict()

    # =========================================================================

    def test_set_schedules(self):
        # Regular list
        blueprint = Blueprint()
        blueprint.schedules = []
        assert isinstance(blueprint.schedules, ScheduleList)

        blueprint.entities.append("locomotive", id="test_train")

        # ScheduleList
        schedule = Schedule()
        schedule.add_locomotive(blueprint.entities["test_train"])
        schedule.append_stop(
            "station_name", WaitCondition(WaitConditionType.INACTIVITY, ticks=600)
        )
        blueprint.schedules = ScheduleList([schedule])
        assert isinstance(blueprint.schedules, ScheduleList)
        assert blueprint.schedules[0].locomotives[0]() is blueprint.entities[0]
        assert blueprint.to_dict()["blueprint"] == {
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
                                    # "compare_type": "or",
                                    "ticks": 600,
                                }
                            ],
                        }
                    ],
                }
            ],
            "version": encode_version(*__factorio_version_info__),
        }

        # None
        blueprint.schedules = None
        assert isinstance(blueprint.schedules, ScheduleList)
        assert blueprint.schedules == ScheduleList()
        assert len(blueprint.schedules) == 0

        with pytest.raises(TypeError):
            blueprint.schedules = dict()

        with pytest.raises(DataFormatError):
            blueprint.schedules = ["incorrect", "format"]

    # =========================================================================

    def test_add_entity(self):
        blueprint = Blueprint()

        # Test merging
        blueprint.entities.append("accumulator")
        blueprint.entities.append("accumulator", merge=True)
        assert len(blueprint.entities) == 1
        assert blueprint.entities[0].to_dict() == {
            "name": "accumulator",
            "position": {"x": 1.0, "y": 1.0},
        }

        # Test broadphase positive, but narrowphase negative
        # TODO: catch warnings
        blueprint = Blueprint()
        blueprint.entities.append("rail-chain-signal")
        blueprint.entities.append("straight-rail", direction=Direction.SOUTHEAST)

        # Unreasonable size
        blueprint = Blueprint()
        blueprint.entities.append("inserter")
        # TODO: reimplement
        # with pytest.raises(UnreasonablySizedBlueprintError):
        #     blueprint.entities.append("inserter", tile_position=(0, 100000))

    def test_change_entity_id(self):
        blueprint = Blueprint()

        blueprint.entities.append("inserter", id="old")
        assert blueprint.entities["old"] is blueprint.entities[0]
        assert blueprint.entities["old"].name == "inserter"

        blueprint.entities["old"] = Container("wooden-chest", id="new")
        assert blueprint.entities["new"] is blueprint.entities[0]
        with pytest.raises(KeyError):
            blueprint.entities["old"]

    def test_move_entity(self):
        blueprint = Blueprint()

        blueprint.entities.append("wooden-chest")

        # TODO: evaluate
        # with pytest.raises(DraftsmanError):
        #     blueprint.entities[0].position = (100.5, 100.5)

        # with pytest.raises(DraftsmanError):
        #     blueprint.entities[0].tile_position = (100, 100)

        # self.assertEqual(blueprint.area, [[100.35, 100.35], [100.65, 100.65]])
        # blueprint.entities.append("inserter")
        # with self.assertRaises(UnreasonablySizedBlueprintError):
        #     blueprint.entities[1].tile_position = (-10_000, -10_000)

    def test_move_tile(self):
        blueprint = Blueprint()

        blueprint.tiles.append("landfill")

        with pytest.raises(DraftsmanError):
            blueprint.tiles[0].position = (100, 100)

    def test_rotate_entity(self):
        blueprint = Blueprint()
        # Inline rotating is permitted when the object is square
        blueprint.entities.append("inserter")
        blueprint.entities[0].direction = Direction.SOUTH
        assert blueprint.entities[0].direction == Direction.SOUTH

        # Setting a 4-way directional object with an 8-way direction results in
        # a warning
        with pytest.warns(DraftsmanWarning):
            blueprint.entities[0].direction = Direction.SOUTHEAST

        # Inline is permitted on non-square objects ONLY when the transformation
        # does not change the apparent tile_width or tile_height
        blueprint.entities[0] = new_entity("splitter", direction=Direction.NORTH)
        blueprint.entities[0].direction = Direction.SOUTH  # equal to flipping
        assert blueprint.entities[0].direction == Direction.SOUTH

        # Inline rotating is not permitted on 8-way rotational objects
        # (similar to how the game handles it)
        # blueprint.entities[0] = new_entity("straight-rail")
        # with pytest.raises(DraftsmanError):
        #     blueprint.entities[0].direction = Direction.SOUTHEAST

    def test_add_tile(self):
        blueprint = Blueprint()
        blueprint.set_version(1, 1, 54, 0)

        # Checkerboard grid
        for x in range(2):
            for y in range(2):
                if (x + y) % 2 == 0:
                    name = "refined-concrete"
                else:
                    name = "refined-hazard-concrete-left"
                blueprint.tiles.append(name, position=(x, y))

        assert blueprint.to_dict()["blueprint"] == {
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
        }

    # =========================================================================

    def test_version_tuple(self):
        blueprint = Blueprint()
        assert blueprint.version_tuple() == __factorio_version_info__
        blueprint.set_version(0, 0, 0, 0)
        assert blueprint.version_tuple() == (0, 0, 0, 0)

    # =========================================================================

    def test_version_string(self):
        blueprint = Blueprint()
        assert blueprint.version_string() == __factorio_version__
        blueprint.set_version(0, 0, 0, 0)
        assert blueprint.version_string() == "0.0.0.0"

    # =========================================================================

    def test_recalculate_area(self):
        blueprint = Blueprint()
        blueprint.entities.append("inserter")
        blueprint.entities.append("inserter", tile_position=(1, 0))
        # TODO: reimplement
        # with pytest.raises(UnreasonablySizedBlueprintError):
        #     blueprint.entities[1] = Container(tile_position=(10002, 0))

    # =========================================================================

    def test_unknown_entities(self):
        blueprint = Blueprint()

        with pytest.raises(InvalidEntityError):
            blueprint.entities.append("some-unknown-entity")
        assert len(blueprint.entities) == 0

        blueprint.entities.append("some-unknown-entity", if_unknown="ignore")
        assert len(blueprint.entities) == 0

        with pytest.warns(UnknownEntityWarning):
            blueprint.entities.append("some-unknown-entity", if_unknown="accept")
        assert len(blueprint.entities) == 1
        assert blueprint.entities[0].name == "some-unknown-entity"

    def test_unknown_tiles(self):
        blueprint = Blueprint()

        with pytest.raises(InvalidTileError):
            blueprint.tiles.append("unknown-tile")
        assert len(blueprint.tiles) == 0

        blueprint.tiles.append("unknown-tile", if_unknown="ignore")
        assert len(blueprint.tiles) == 0

        with pytest.warns(UnknownTileWarning):
            blueprint.tiles.append("unknown-tile", if_unknown="accept")
        assert len(blueprint.tiles) == 1
        assert blueprint.tiles[0].name == "unknown-tile"

    # =========================================================================

    def test_tile_copying(self):
        blueprint = Blueprint()

        concrete = Tile("concrete")  # (0, 0)

        blueprint.tiles.append(
            concrete, copy=True, position=(10, 10)
        )  # copy new position over copied tile
        assert len(blueprint.tiles) == 1
        assert blueprint.tiles[0].name == "concrete"
        assert blueprint.tiles[0].position == Vector(10, 10)

        # Merge a non-copy (prohibited)
        with pytest.raises(ValueError):
            blueprint.tiles.append(concrete, copy=False, merge=True, position=(10, 10))

    # =========================================================================

    def test_to_dict(self):
        # List case
        blueprint = Blueprint()
        assert blueprint.to_dict()["blueprint"] == {
            "item": "blueprint",
            "version": encode_version(*__factorio_version_info__),
        }
        # TODO: fix, ideally
        # assert blueprint.entities is blueprint._root["blueprint"]["entities"]
        # assert blueprint.tiles is blueprint._root["blueprint"]["tiles"]
        # assert blueprint.schedules is blueprint._root["blueprint"]["schedules"]

        # Copper wire connection case
        blueprint.entities.append("power-switch", id="a")
        blueprint.entities.append("small-electric-pole", tile_position=(5, 0), id="b")
        blueprint.add_power_connection("a", "b", 1)
        blueprint.tiles.append("landfill")
        blueprint.snapping_grid_position = (-1, -1)  # also test this
        self.maxDiff = None
        assert blueprint.to_dict()["blueprint"] == {
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
        }

        # Non-string id connection case
        example_string = "0eNqdkkFuwyAQRe8yaxwZUscp2x6jsiLbmSYjYUCA61oWdy84VRXJ3rQbxEcz/z/NsECnRrSOdAC5APVGe5DvC3i66VbltzBbBAkUcAAGuh2ysmZCV/iJQn+HyID0Fb9A8tgwQB0oED58VjFf9Dh06FLBr4MfWqUKVNgHR31hjcJkb41PvUbn4OzHq0PFYAZZnM6HKgUlQJ1aaOVcgOfD4fU5i5ISsYmpWiPd7p0ZXYYRTWQbIPFHICH+B8R3gPge0HF/xjsk5Q9HvaV4G/lmIgwmcrjeywTD4OF88aENKe6jVR7z+tZFy6d/weATnV+TxZm/1K+irnjFj6cyxm8HML+f"
        blueprint.load_from_string(example_string)
        self.maxDiff = None
        assert blueprint.to_dict()["blueprint"] == {
            "item": "blueprint",
            "icons": [{"index": 1, "signal": {"name": "power-switch", "type": "item"}}],
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
                    # "switch_state": False, # Default
                    "entity_number": 3,
                },
            ],
            "version": encode_version(1, 1, 53, 0),
        }

        # Numeric Locomotive case
        bp_string = "0eNqN091ugjAUB/BXMee6GopWlNtd7gmWxZgKJ3IyaElb3Izh3dda4oghjnBDP86vp+HPDU51h60h5SC/ARVaWcg/b2DprGQd5ty1RciBHDbAQMkmjIykGnoGpEr8gZz37N+SWhe60Y4uOCpM+wMDVI4cYTz4PrgeVdec0Hh5qp5Bq60v0SqcFs7nWwZXyJci87Y25BUZ15NVKkJ3T276cK3zlzlXbnm/0wS9HtElGSziajqhruerYr66ma9m81UxX93PV7cPNaBqaZ1uX5HiiWS+m+HLwZvB0JZWi/fV4kOqopIGQmBsUWHZ1UNi/oIRxny0HpP82mPwLckdffDLe4fR9GIrDR6HJOuwb3h31IQEOiq+/F6+S5L+EB4W856P/igGFzQ2XmzHN9k+zQQXfL1N+v4XYYYmCA=="
        blueprint.load_from_string(bp_string)
        assert blueprint.to_dict()["blueprint"] == {
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
                                    # "compare_type": "or",
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
        }

        # Nested List case
        blueprint = Blueprint()
        group = Group("test")
        group.entities.append(Container("wooden-chest"))
        blueprint.entities.append(group)
        blueprint.tiles.append("refined-concrete")
        assert blueprint.to_dict()["blueprint"] == {
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
        }

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
            def collision_set(self):  # pragma: no coverage
                return CollisionSet([])

            @property
            def collision_mask(self):  # pragma: no coverage
                return set()

            @property
            def tile_width(self):  # pragma: no coverage
                return 1

            @property
            def tile_height(self):  # pragma: no coverage
                return 1

            def inspect(self):  # pragma: no coverage
                pass

            def mergable_with(self, other):  # pragma: no coverage
                return False

            def merge(self, other):  # pragma: no coverage
                return self

            def to_dict(self):  # pragma: no coverage
                return "incorrect"

        test = TestClass()
        blueprint.entities.append(test)
        with pytest.raises(DraftsmanError):
            blueprint.to_dict()

    # =========================================================================

    def test_getitem(self):
        blueprint = Blueprint()
        blueprint.label = "testing"
        assert blueprint["blueprint"]["label"] is blueprint._root["blueprint"]["label"]

    # =========================================================================

    def test_setitem(self):
        blueprint = Blueprint()
        blueprint["blueprint"]["label"] = "testing"
        assert blueprint["blueprint"]["label"] is blueprint._root["blueprint"]["label"]

    # =========================================================================

    def test_contains(self):
        blueprint = Blueprint()
        blueprint["label"] = "testing"
        assert ("label" in blueprint["blueprint"]) == True

    def test_deepcopy(self):
        blueprint = Blueprint()

        blueprint.entities.append("wooden-chest", id="test container")

        group = Group("powerlines")
        group.entities.append("small-electric-pole")
        group.entities.append("small-electric-pole", tile_position=(5, 0))
        group.add_circuit_connection("red", 0, 1)
        group.add_power_connection(0, 1)
        group.position = (0, 1)

        blueprint.entities.append(group)
        blueprint.add_circuit_connection("green", "test container", ("powerlines", 0))

        # Entities
        assert blueprint.entities[0].parent is blueprint
        assert (
            blueprint.entities[("powerlines", 0)].parent
            is blueprint.entities["powerlines"]
        )
        assert (
            blueprint.entities[("powerlines", 1)].parent
            is blueprint.entities["powerlines"]
        )
        assert blueprint.entities["powerlines"].parent is blueprint
        # Outcome
        assert blueprint.to_dict()["blueprint"] == {
            "item": "blueprint",
            "entities": [
                {
                    "name": "wooden-chest",
                    "position": {"x": 0.5, "y": 0.5},
                    "connections": {"1": {"green": [{"entity_id": 2}]}},
                    "entity_number": 1,
                },
                {
                    "name": "small-electric-pole",
                    "position": {"x": 0.5, "y": 1.5},
                    "connections": {
                        "1": {
                            "red": [{"entity_id": 3}],
                            "green": [{"entity_id": 1}],
                        }
                    },
                    "neighbours": [3],
                    "entity_number": 2,
                },
                {
                    "name": "small-electric-pole",
                    "position": {"x": 5.5, "y": 1.5},
                    "connections": {"1": {"red": [{"entity_id": 2}]}},
                    "neighbours": [2],
                    "entity_number": 3,
                },
            ],
            "version": encode_version(*__factorio_version_info__),
        }

        # Create a deepcopy of blueprint
        import copy

        blueprint_copy = copy.deepcopy(blueprint)
        # Entities
        assert blueprint_copy.entities[0].parent is blueprint_copy
        assert (
            blueprint_copy.entities[("powerlines", 0)].parent
            is blueprint_copy.entities["powerlines"]
        )
        assert (
            blueprint_copy.entities[("powerlines", 1)].parent
            is blueprint_copy.entities["powerlines"]
        )
        assert blueprint_copy.entities["powerlines"].parent is blueprint_copy

        # Outcome
        assert blueprint_copy.to_dict()["blueprint"] == {
            "item": "blueprint",
            "entities": [
                {
                    "name": "wooden-chest",
                    "position": {"x": 0.5, "y": 0.5},
                    "connections": {"1": {"green": [{"entity_id": 2}]}},
                    "entity_number": 1,
                },
                {
                    "name": "small-electric-pole",
                    "position": {"x": 0.5, "y": 1.5},
                    "connections": {
                        "1": {
                            "red": [{"entity_id": 3}],
                            "green": [{"entity_id": 1}],
                        }
                    },
                    "neighbours": [3],
                    "entity_number": 2,
                },
                {
                    "name": "small-electric-pole",
                    "position": {"x": 5.5, "y": 1.5},
                    "connections": {"1": {"red": [{"entity_id": 2}]}},
                    "neighbours": [2],
                    "entity_number": 3,
                },
            ],
            "version": encode_version(*__factorio_version_info__),
        }

    # =========================================================================
    # EntityCollection
    # =========================================================================

    def test_find_entity(self):
        # Blueprint search case
        blueprint = Blueprint()
        blueprint.entities.append("wooden-chest", tile_position=(1, 1))
        blueprint.entities.append("iron-chest", tile_position=(5, 0))
        blueprint.entities.append("steel-chest", tile_position=(10, 10))

        found_entity = blueprint.find_entity("wooden-chest", (1.5, 1.5))
        assert found_entity is blueprint.entities[0]

        found_entity = blueprint.find_entity("something-else", (1.5, 1.5))
        assert found_entity is None

        # Group search case
        group = Group("test", position=(-5, -5))
        group.entities.append("wooden-chest", tile_position=(-5, -5))
        blueprint.entities.append(group)
        # Incorrect
        found_entity = blueprint.find_entity("wooden-chest", (-4.5, -4.5))
        assert found_entity is None
        # Correct
        found_entity = blueprint.find_entity("wooden-chest", (-9.5, -9.5))
        assert found_entity is blueprint.entities[("test", 0)]

    # =========================================================================

    def test_find_entity_at_position(self):
        # Blueprint search case
        blueprint = Blueprint()
        blueprint.entities.append("wooden-chest", tile_position=(1, 1))
        blueprint.entities.append("iron-chest", tile_position=(5, 0))
        blueprint.entities.append("steel-chest", tile_position=(10, 10))

        found_entity = blueprint.find_entity_at_position((1.5, 1.5))
        assert found_entity is blueprint.entities[0]

        # Group search case
        group = Group("test", position=(-5, -5))
        group.entities.append("wooden-chest", tile_position=(-5, -5))
        blueprint.entities.append(group)
        # Incorrect
        found_entity = blueprint.find_entity_at_position((-4.5, -4.5))
        assert found_entity is None
        # Correct
        found_entity = blueprint.find_entity_at_position((-9.5, -9.5))
        assert found_entity is blueprint.entities[("test", 0)]

    def test_find_entities(self):
        blueprint = Blueprint()
        blueprint.entities.append("wooden-chest", tile_position=(1, 1))
        blueprint.entities.append("iron-chest", tile_position=(5, 0))
        blueprint.entities.append("steel-chest", tile_position=(10, 10))

        found_entities = blueprint.find_entities()
        assert found_entities == blueprint.entities._root

        # Explicit AABB
        found_entities = blueprint.find_entities(AABB(0, 0, 6, 6))
        assert found_entities == [blueprint.entities[0], blueprint.entities[1]]

        # Implicit AABB
        found_entities = blueprint.find_entities([0, 0, 6, 6])

        # Group search case
        group = Group("test", position=(-5, -5))
        group.entities.append("wooden-chest", tile_position=(-5, -5))
        blueprint.entities.append(group)
        # Unchanged
        found_entities = blueprint.find_entities()
        assert found_entities == blueprint.entities._root
        # Unchanged
        found_entities = blueprint.find_entities([0, 0, 6, 6])
        assert found_entities == [blueprint.entities[0], blueprint.entities[1]]
        # Entity group
        found_entities = blueprint.find_entities([-10, -10, 0, 0])
        assert found_entities == [blueprint.entities[("test", 0)]]

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
        assert found == blueprint.entities._root

        # Limit
        found = blueprint.find_entities_filtered(limit=2)
        assert found == [blueprint.entities[0], blueprint.entities[1]]

        # Position
        found = blueprint.find_entities_filtered(position=(1.5, 1.5))
        assert found == [blueprint.entities[0]]

        # Position + Radius
        found = blueprint.find_entities_filtered(position=(0, 0), radius=10)
        assert found == [
            blueprint.entities[0],
            blueprint.entities[1],
            blueprint.entities[3],
        ]

        # Area
        found = blueprint.find_entities_filtered(area=[4, -1, 11, 11])
        assert found == [
            blueprint.entities[1],
            blueprint.entities[3],
            blueprint.entities[2],
        ]

        # Name
        found = blueprint.find_entities_filtered(name="wooden-chest")
        assert found == [blueprint.entities[0]]

        # Names
        found = blueprint.find_entities_filtered(
            name={"wooden-chest", "decider-combinator"}
        )
        assert found == [blueprint.entities[0], blueprint.entities[1]]

        # Type
        found = blueprint.find_entities_filtered(type="container")
        assert found == [blueprint.entities[0], blueprint.entities[2]]

        # Types
        found = blueprint.find_entities_filtered(
            type={"container", "decider-combinator", "arithmetic-combinator"}
        )
        assert found == blueprint.entities._root

        # Direction
        found = blueprint.find_entities_filtered(direction=Direction.NORTH)
        assert found == [blueprint.entities[1]]

        # Directions
        found = blueprint.find_entities_filtered(
            direction={Direction.NORTH, Direction.SOUTH}
        )
        assert found == [blueprint.entities[1], blueprint.entities[3]]

        # Invert
        found = blueprint.find_entities_filtered(
            direction={Direction.NORTH, Direction.SOUTH}, invert=True
        )
        assert found == [blueprint.entities[0], blueprint.entities[2]]

        # Group search case
        blueprint.entities = None
        group = Group("test")
        group.entities.append("transport-belt")
        blueprint.entities.append(group)
        found = blueprint.find_entities_filtered()
        assert found == [blueprint.entities[("test", 0)]]

    # =========================================================================

    def test_power_connections(self):
        blueprint = Blueprint()

        blueprint.entities.append("substation", id="1")
        blueprint.entities.append("substation", tile_position=(6, 0), id="2")

        blueprint.add_power_connection("1", "2")
        self.maxDiff = None
        assert blueprint.to_dict()["blueprint"] == {
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
        }

        blueprint.remove_power_connection("2", "1")
        assert blueprint.to_dict()["blueprint"] == {
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
        }

        # Test direct references
        # Create some easy variable names
        substationA = blueprint.entities[0]
        substationB = blueprint.entities[1]

        blueprint.add_power_connection(substationA, substationB)
        assert blueprint.to_dict()["blueprint"] == {
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
        }
        blueprint.remove_power_connection(substationB, substationA)
        assert blueprint.to_dict()["blueprint"] == {
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
        }

        # Test entity not in blueprint
        substationC = ElectricPole("substation")
        with pytest.raises(InvalidAssociationError):
            blueprint.add_power_connection(substationA, substationC)
        with pytest.raises(InvalidAssociationError):
            blueprint.add_power_connection(substationC, substationB)

        with pytest.raises(InvalidAssociationError):
            blueprint.remove_power_connection(substationA, substationC)
        with pytest.raises(InvalidAssociationError):
            blueprint.remove_power_connection(substationC, substationB)

        # Errors
        blueprint.entities.append("power-switch", tile_position=(10, 10), id="p")

        with pytest.raises(InvalidConnectionSideError):
            blueprint.add_power_connection("1", "p", 3)

        blueprint.entities.append("radar", tile_position=(0, 6), id="3")

        with pytest.raises(EntityNotPowerConnectableError):
            blueprint.add_power_connection("3", "1")
        with pytest.raises(EntityNotPowerConnectableError):
            blueprint.add_power_connection("1", "3")

        # Test max connections
        blueprint.entities = None
        blueprint.entities.append("substation")
        for i in range(6):
            blueprint.entities.append("substation", tile_position=((i - 3) * 2, -2))
        for i in range(5):
            blueprint.add_power_connection(0, i + 1)
        with pytest.warns(TooManyConnectionsWarning):
            blueprint.add_power_connection(0, 6)
        with pytest.warns(TooManyConnectionsWarning):
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
        assert blueprint.to_dict() == {
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
        }
        blueprint.remove_power_connections()
        assert blueprint.to_dict() == {
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
        }

        # Test recursive power connections
        blueprint = Blueprint()
        group = Group("group")
        group.entities.append("small-electric-pole")
        group.entities.append("small-electric-pole", tile_position=(1, 1))
        group.add_power_connection(0, 1)
        blueprint.entities.append(group)
        blueprint.entities.append(
            "small-electric-pole", tile_position=(2, 2), id="root"
        )
        blueprint.add_power_connection("root", ("group", 1))
        assert blueprint.to_dict()["blueprint"] == {
            "item": "blueprint",
            "entities": [
                {
                    "entity_number": 1,
                    "name": "small-electric-pole",
                    "position": {"x": 0.5, "y": 0.5},
                    "neighbours": [2],
                },
                {
                    "entity_number": 2,
                    "name": "small-electric-pole",
                    "position": {"x": 1.5, "y": 1.5},
                    "neighbours": [1, 3],
                },
                {
                    "entity_number": 3,
                    "name": "small-electric-pole",
                    "position": {"x": 2.5, "y": 2.5},
                    "neighbours": [2],
                },
            ],
            "version": encode_version(*__factorio_version_info__),
        }

        blueprint.remove_power_connections()

        assert blueprint.to_dict()["blueprint"] == {
            "item": "blueprint",
            "entities": [
                {
                    "entity_number": 1,
                    "name": "small-electric-pole",
                    "position": {"x": 0.5, "y": 0.5},
                },
                {
                    "entity_number": 2,
                    "name": "small-electric-pole",
                    "position": {"x": 1.5, "y": 1.5},
                },
                {
                    "entity_number": 3,
                    "name": "small-electric-pole",
                    "position": {"x": 2.5, "y": 2.5},
                },
            ],
            "version": encode_version(*__factorio_version_info__),
        }

    # =========================================================================

    def test_generate_power_connections(self):
        blueprint = Blueprint()
        assert blueprint.to_dict() == {
            "blueprint": {
                "item": "blueprint",
                "version": encode_version(*__factorio_version_info__),
            }
        }
        # Null case
        blueprint.generate_power_connections()
        assert blueprint.to_dict() == {
            "blueprint": {
                "item": "blueprint",
                "version": encode_version(*__factorio_version_info__),
            }
        }
        # Normal case
        pole = ElectricPole("medium-electric-pole")
        for i in range(4):
            pole.tile_position = ((i % 2) * 4, int(i / 2) * 4)
            blueprint.entities.append(pole)
        pole.tile_position = (2, 2)
        blueprint.entities.append(pole)
        self.maxDiff = None
        assert blueprint.to_dict() == {
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
        }
        blueprint.generate_power_connections()
        assert blueprint.to_dict() == {
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
        }
        # Test only_axis
        blueprint.remove_power_connections()
        blueprint.generate_power_connections(only_axis=True)
        assert blueprint.to_dict() == {
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
        }
        # Test prefer_axis
        blueprint.entities = None
        blueprint.entities.append("medium-electric-pole")
        blueprint.entities.append("medium-electric-pole", tile_position=(5, 0))
        blueprint.entities.append("medium-electric-pole", tile_position=(1, 1))
        blueprint.generate_power_connections(prefer_axis=False)
        assert blueprint.to_dict() == {
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
        }

        # Test too many power connections
        blueprint.entities = None
        for i in range(3):
            blueprint.entities.append("medium-electric-pole", tile_position=(0, i))
            blueprint.entities.append("medium-electric-pole", tile_position=(3, i))
        blueprint.generate_power_connections()

    # =========================================================================

    def test_circuit_connections(self):
        blueprint = Blueprint()

        blueprint.entities.append("substation", id="1")
        blueprint.entities.append("substation", tile_position=(6, 0), id="2")

        blueprint.add_circuit_connection("red", "1", "2")
        self.maxDiff = None
        assert blueprint.to_dict()["blueprint"] == {
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
        }

        blueprint.remove_circuit_connection("red", "2", "1")
        assert blueprint.to_dict()["blueprint"] == {
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
        }

        # Test direct references
        # Create some easy variable names
        substationA = blueprint.entities[0]
        substationB = blueprint.entities[1]

        blueprint.add_circuit_connection("green", substationA, substationB)
        assert blueprint.to_dict()["blueprint"] == {
            "item": "blueprint",
            "entities": [
                {
                    "name": "substation",
                    "position": {"x": 1.0, "y": 1.0},
                    "connections": {"1": {"green": [{"entity_id": 2}]}},
                    "entity_number": 1,
                },
                {
                    "name": "substation",
                    "position": {"x": 7.0, "y": 1.0},
                    "connections": {"1": {"green": [{"entity_id": 1}]}},
                    "entity_number": 2,
                },
            ],
            "version": encode_version(*__factorio_version_info__),
        }
        blueprint.remove_circuit_connection("green", substationB, substationA)
        assert blueprint.to_dict()["blueprint"] == {
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
        }

        # Test entity not in blueprint
        substationC = ElectricPole("substation")
        with pytest.raises(InvalidAssociationError):
            blueprint.add_circuit_connection("red", substationA, substationC)
        with pytest.raises(InvalidAssociationError):
            blueprint.add_circuit_connection("red", substationC, substationB)

        with pytest.raises(InvalidAssociationError):
            blueprint.remove_circuit_connection("red", substationA, substationC)
        with pytest.raises(InvalidAssociationError):
            blueprint.remove_circuit_connection("red", substationC, substationB)

        # Test adjacent gate warning
        # TODO

        # Errors
        blueprint.entities.append("radar", tile_position=(0, 6), id="3")

        with pytest.raises(EntityNotCircuitConnectableError):
            blueprint.add_circuit_connection("green", "3", "1")
        with pytest.raises(EntityNotCircuitConnectableError):
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
        assert blueprint.to_dict() == {
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
        }
        blueprint.remove_circuit_connections()
        assert blueprint.to_dict() == {
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
        }

        # Remove recursive circuit connections
        blueprint = Blueprint()
        group = Group("group")
        group.entities.append("transport-belt")
        group.entities.append("transport-belt", tile_position=(1, 1))
        group.add_circuit_connection("red", 0, 1)
        blueprint.entities.append(group)
        blueprint.entities.append("transport-belt", tile_position=(2, 2), id="root")
        blueprint.add_circuit_connection("green", "root", ("group", 1))
        assert blueprint.to_dict()["blueprint"] == {
            "item": "blueprint",
            "entities": [
                {
                    "entity_number": 1,
                    "name": "transport-belt",
                    "position": {"x": 0.5, "y": 0.5},
                    "connections": {"1": {"red": [{"entity_id": 2}]}},
                },
                {
                    "entity_number": 2,
                    "name": "transport-belt",
                    "position": {"x": 1.5, "y": 1.5},
                    "connections": {
                        "1": {
                            "red": [{"entity_id": 1}],
                            "green": [{"entity_id": 3}],
                        }
                    },
                },
                {
                    "entity_number": 3,
                    "name": "transport-belt",
                    "position": {"x": 2.5, "y": 2.5},
                    "connections": {"1": {"green": [{"entity_id": 2}]}},
                },
            ],
            "version": encode_version(*__factorio_version_info__),
        }

        blueprint.remove_circuit_connections()

        assert blueprint.to_dict()["blueprint"] == {
            "item": "blueprint",
            "entities": [
                {
                    "entity_number": 1,
                    "name": "transport-belt",
                    "position": {"x": 0.5, "y": 0.5},
                },
                {
                    "entity_number": 2,
                    "name": "transport-belt",
                    "position": {"x": 1.5, "y": 1.5},
                },
                {
                    "entity_number": 3,
                    "name": "transport-belt",
                    "position": {"x": 2.5, "y": 2.5},
                },
            ],
            "version": encode_version(*__factorio_version_info__),
        }

    # =========================================================================
    # Trains
    # =========================================================================

    def test_add_train_at_position(self):
        # Without schedule
        blueprint = Blueprint()

        config = TrainConfiguration("1-1")

        blueprint.add_train_at_position(
            config=config, position=(0, 0), direction=Direction.WEST
        )

        assert len(blueprint.entities) == 2
        assert blueprint.to_dict()["blueprint"] == {
            "item": "blueprint",
            "entities": [
                {
                    "name": "locomotive",
                    "orientation": Orientation.WEST,
                    "position": {"x": 0.0, "y": 0.0},
                    "entity_number": 1,
                },
                {
                    "name": "cargo-wagon",
                    "orientation": Orientation.WEST,
                    "position": {"x": 7.0, "y": 0.0},
                    "entity_number": 2,
                },
            ],
            "version": encode_version(*__factorio_version_info__),
        }

        # With schedule
        schedule = Schedule()
        schedule.append_stop("Station 1", WaitCondition(WaitConditionType.FULL_CARGO))
        schedule.append_stop("Station 2", WaitCondition(WaitConditionType.EMPTY_CARGO))

        # (Also test string configuration)
        blueprint.add_train_at_position(
            config="1-1", position=(0, 2), direction=Direction.EAST, schedule=schedule
        )

        assert len(blueprint.entities) == 4
        assert blueprint.to_dict()["blueprint"] == {
            "item": "blueprint",
            "entities": [
                {
                    "name": "locomotive",
                    "orientation": Orientation.WEST,
                    "position": {"x": 0.0, "y": 0.0},
                    "entity_number": 1,
                },
                {
                    "name": "cargo-wagon",
                    "orientation": Orientation.WEST,
                    "position": {"x": 7.0, "y": 0.0},
                    "entity_number": 2,
                },
                {
                    "name": "locomotive",
                    "orientation": Orientation.EAST,
                    "position": {"x": 0.0, "y": 2.0},
                    "entity_number": 3,
                },
                {
                    "name": "cargo-wagon",
                    "orientation": Orientation.EAST,
                    "position": {"x": -7.0, "y": 2.0},
                    "entity_number": 4,
                },
            ],
            "schedules": [
                {
                    "locomotives": [3],
                    "schedule": [
                        {
                            "station": "Station 1",
                            "wait_conditions": [
                                {
                                    "type": WaitConditionType.FULL_CARGO,
                                    # "compare_type": WaitConditionCompareType.OR,
                                }
                            ],
                        },
                        {
                            "station": "Station 2",
                            "wait_conditions": [
                                {
                                    "type": WaitConditionType.EMPTY_CARGO,
                                    # "compare_type": WaitConditionCompareType.OR,
                                }
                            ],
                        },
                    ],
                }
            ],
            "version": encode_version(*__factorio_version_info__),
        }

        # Ensure new trains with same schedule dont create duplicate schedules
        blueprint.add_train_at_position(
            config=config, position=(0, 4), direction=Direction.EAST, schedule=schedule
        )
        assert len(blueprint.entities) == 6
        assert blueprint.to_dict()["blueprint"]["schedules"] == [
            {
                "locomotives": [3, 5],
                "schedule": [
                    {
                        "station": "Station 1",
                        "wait_conditions": [
                            {
                                "type": WaitConditionType.FULL_CARGO,
                                # "compare_type": WaitConditionCompareType.OR,
                            }
                        ],
                    },
                    {
                        "station": "Station 2",
                        "wait_conditions": [
                            {
                                "type": WaitConditionType.EMPTY_CARGO,
                                # "compare_type": WaitConditionCompareType.OR,
                            }
                        ],
                    },
                ],
            }
        ]

        # Ensure trains with different schedules actually create new schedules
        schedule = Schedule()
        schedule.append_stop("Station 3", WaitCondition(WaitConditionType.FULL_CARGO))
        schedule.append_stop("Station 4", WaitCondition(WaitConditionType.EMPTY_CARGO))

        blueprint.add_train_at_position(
            config=config, position=(0, 6), direction=Direction.EAST, schedule=schedule
        )
        assert len(blueprint.entities) == 8
        assert blueprint.to_dict()["blueprint"]["schedules"] == [
            {
                "locomotives": [3, 5],
                "schedule": [
                    {
                        "station": "Station 1",
                        "wait_conditions": [
                            {
                                "type": WaitConditionType.FULL_CARGO,
                                # "compare_type": WaitConditionCompareType.OR,
                            }
                        ],
                    },
                    {
                        "station": "Station 2",
                        "wait_conditions": [
                            {
                                "type": WaitConditionType.EMPTY_CARGO,
                                # "compare_type": WaitConditionCompareType.OR,
                            }
                        ],
                    },
                ],
            },
            {
                "locomotives": [7],
                "schedule": [
                    {
                        "station": "Station 3",
                        "wait_conditions": [
                            {
                                "type": WaitConditionType.FULL_CARGO,
                                # "compare_type": WaitConditionCompareType.OR,
                            }
                        ],
                    },
                    {
                        "station": "Station 4",
                        "wait_conditions": [
                            {
                                "type": WaitConditionType.EMPTY_CARGO,
                                # "compare_type": WaitConditionCompareType.OR,
                            }
                        ],
                    },
                ],
            },
        ]

    # =========================================================================

    def test_add_train_at_station(self):
        # Without schedule
        blueprint = Blueprint()

        blueprint.entities.append(
            "train-stop", direction=Direction.WEST, station="Station 1", id="Station 1"
        )

        config = TrainConfiguration("1-1")

        blueprint.add_train_at_station(config=config, station="Station 1")

        assert len(blueprint.entities) == 3
        assert blueprint.to_dict()["blueprint"] == {
            "item": "blueprint",
            "entities": [
                {
                    "name": "train-stop",
                    "direction": Direction.WEST,
                    "position": {"x": 1.0, "y": 1.0},
                    "station": "Station 1",
                    "entity_number": 1,
                },
                {
                    "name": "locomotive",
                    "orientation": Orientation.WEST,
                    "position": {"x": 5.0, "y": 3.0},
                    "entity_number": 2,
                },
                {
                    "name": "cargo-wagon",
                    "orientation": Orientation.WEST,
                    "position": {"x": 12.0, "y": 3.0},
                    "entity_number": 3,
                },
            ],
            "version": encode_version(*__factorio_version_info__),
        }

        # With schedule
        blueprint.entities.append(
            "train-stop",
            position=(1.0, 7.0),
            direction=Direction.EAST,
            station="Station 2",
            id="Station 2",
        )

        schedule = Schedule()
        schedule.append_stop("Station 1", WaitCondition(WaitConditionType.FULL_CARGO))
        schedule.append_stop("Station 2", WaitCondition(WaitConditionType.EMPTY_CARGO))

        # Test direct reference and string config
        blueprint.add_train_at_station(
            config="1-1", station=blueprint.entities[-1], schedule=schedule
        )

        assert len(blueprint.entities) == 6
        assert blueprint.to_dict()["blueprint"] == {
            "item": "blueprint",
            "entities": [
                {
                    "name": "train-stop",
                    "direction": Direction.WEST,
                    "position": {"x": 1.0, "y": 1.0},
                    "station": "Station 1",
                    "entity_number": 1,
                },
                {
                    "name": "locomotive",
                    "orientation": Orientation.WEST,
                    "position": {"x": 5.0, "y": 3.0},
                    "entity_number": 2,
                },
                {
                    "name": "cargo-wagon",
                    "orientation": Orientation.WEST,
                    "position": {"x": 12.0, "y": 3.0},
                    "entity_number": 3,
                },
                {
                    "name": "train-stop",
                    "direction": Direction.EAST,
                    "position": {"x": 1.0, "y": 7.0},
                    "station": "Station 2",
                    "entity_number": 4,
                },
                {
                    "name": "locomotive",
                    "orientation": Orientation.EAST,
                    "position": {"x": -3.0, "y": 5.0},
                    "entity_number": 5,
                },
                {
                    "name": "cargo-wagon",
                    "orientation": Orientation.EAST,
                    "position": {"x": -10.0, "y": 5.0},
                    "entity_number": 6,
                },
            ],
            "schedules": [
                {
                    "locomotives": [5],
                    "schedule": [
                        {
                            "station": "Station 1",
                            "wait_conditions": [
                                {
                                    "type": WaitConditionType.FULL_CARGO,
                                    # "compare_type": WaitConditionCompareType.OR,
                                }
                            ],
                        },
                        {
                            "station": "Station 2",
                            "wait_conditions": [
                                {
                                    "type": WaitConditionType.EMPTY_CARGO,
                                    # "compare_type": WaitConditionCompareType.OR,
                                }
                            ],
                        },
                    ],
                }
            ],
            "version": encode_version(*__factorio_version_info__),
        }

        # Ensure new trains with same schedule dont create duplicate schedules
        blueprint.entities.append(
            "train-stop",
            direction=Direction.NORTH,
            position=(9.0, 9.0),
            station="Station 3",
        )

        blueprint.add_train_at_station(
            config=config, station=blueprint.entities[-1], schedule=schedule
        )
        assert len(blueprint.entities) == 9
        assert blueprint.to_dict()["blueprint"]["schedules"] == [
            {
                "locomotives": [5, 8],
                "schedule": [
                    {
                        "station": "Station 1",
                        "wait_conditions": [
                            {
                                "type": WaitConditionType.FULL_CARGO,
                                # "compare_type": WaitConditionCompareType.OR,
                            }
                        ],
                    },
                    {
                        "station": "Station 2",
                        "wait_conditions": [
                            {
                                "type": WaitConditionType.EMPTY_CARGO,
                                # "compare_type": WaitConditionCompareType.OR,
                            }
                        ],
                    },
                ],
            }
        ]

        # Ensure trains with different schedules actually create new schedules
        schedule = Schedule()
        schedule.append_stop("Station 3", WaitCondition(WaitConditionType.FULL_CARGO))
        schedule.append_stop("Station 4", WaitCondition(WaitConditionType.EMPTY_CARGO))

        blueprint.entities.append(
            "train-stop",
            direction=Direction.NORTH,
            position=(19.0, 9.0),
            station="Station 4",
        )

        blueprint.add_train_at_station(
            config=config, station=blueprint.entities[-1], schedule=schedule
        )
        assert len(blueprint.entities) == 12
        assert blueprint.to_dict()["blueprint"]["schedules"] == [
            {
                "locomotives": [5, 8],
                "schedule": [
                    {
                        "station": "Station 1",
                        "wait_conditions": [
                            {
                                "type": WaitConditionType.FULL_CARGO,
                                # "compare_type": WaitConditionCompareType.OR,
                            }
                        ],
                    },
                    {
                        "station": "Station 2",
                        "wait_conditions": [
                            {
                                "type": WaitConditionType.EMPTY_CARGO,
                                # "compare_type": WaitConditionCompareType.OR,
                            }
                        ],
                    },
                ],
            },
            {
                "locomotives": [11],
                "schedule": [
                    {
                        "station": "Station 3",
                        "wait_conditions": [
                            {
                                "type": WaitConditionType.FULL_CARGO,
                                # "compare_type": WaitConditionCompareType.OR,
                            }
                        ],
                    },
                    {
                        "station": "Station 4",
                        "wait_conditions": [
                            {
                                "type": WaitConditionType.EMPTY_CARGO,
                                # "compare_type": WaitConditionCompareType.OR,
                            }
                        ],
                    },
                ],
            },
        ]

        # Ensure train stop is an actual train stop
        blueprint.entities.append("transport-belt", tile_position=(-10, -10))
        with pytest.raises(ValueError, match="'station' must be a TrainStop"):
            blueprint.add_train_at_station(
                config=config, station=blueprint.entities[-1]
            )

    # =========================================================================

    def test_set_train_schedule(self):
        # 2 trains with 2 different schedules
        test_string = "0eNqdk01vgzAMhv+Lz1lVvkrh3MOOO2+qUApuFykkURK6oYr/PhPY1k2dVHaLkf08rxJzgYPs0FihPJQXELVWDsqXCzhxUlyO33xvEEoQHltgoHg7VlLXutVenBEGBkI1+A5lNLD/DcbDngEqL7zASR+KvlJde0BL5FvzDIx2NKLVaCPMQ5Yx6KHcrIpisy6SPCOFtoJgfGpbr7Ix4y96fB89LQI9vw+aLIocJQszp4syR+ktKl26q1+x6eR869+osY5YctUxbcXnODwib8j3xoWvaGmaYJ0oxDDcYjW/v7bUN5+PnZQw7MOefKF2Vht9PC6nYWt8P+IC8Gf4mKV/h3/i8oz2ebnRcOdQndBWxiKd/GQnU9jy8upvYkAKF3zxNkrzIs7zJC+ybToMH2rsKd8="
        blueprint = Blueprint(test_string)
        # Also add another dummy schedule before
        # blueprint.schedules.insert(0, Schedule())

        trains = blueprint.find_trains_filtered()
        assert len(trains) == 2
        train = trains[0]
        assert len(blueprint.schedules) == 2
        assert len(blueprint.schedules[0].locomotives) == 2
        assert blueprint.schedules[0].locomotives[0]() in train

        # Set train schedule to None
        blueprint.set_train_schedule(train, None)
        assert len(blueprint.schedules) == 2
        assert len(blueprint.schedules[0].locomotives) == 0

        # Doing it again should have no ill effects
        blueprint.set_train_schedule(train, None)
        assert len(blueprint.schedules) == 2
        assert len(blueprint.schedules[0].locomotives) == 0

        # Delete any schedules with no locomotives, which should delete 1 schedule
        blueprint.schedules[:] = [
            schedule
            for schedule in blueprint.schedules
            if len(schedule.locomotives) > 0
        ]
        assert len(blueprint.schedules) == 1

        # Set the first train's schedule to that of the second
        # (Also test selection with just one train car)
        blueprint.set_train_schedule(train[0], blueprint.schedules[0])
        assert len(blueprint.schedules[0].locomotives) == 4
        assert blueprint.schedules[0].locomotives[2]() in train

        # Overwrite the first train's schedule with a new schedule
        new_schedule = Schedule()
        new_schedule.append_stop("new stop 1")
        new_schedule.append_stop("new stop 2")
        blueprint.set_train_schedule(train, new_schedule)

        assert len(blueprint.schedules) == 2
        assert len(blueprint.schedules[0].locomotives) == 2
        assert len(blueprint.schedules[1].locomotives) == 2
        assert blueprint.schedules[1].locomotives[0]() in train

    # =========================================================================

    def test_remove_train(self):
        blueprint = Blueprint()

        config = TrainConfiguration("1-1")
        schedule1 = Schedule()
        schedule1.append_stop("Station 1", WaitCondition(WaitConditionType.FULL_CARGO))

        schedule2 = Schedule()
        schedule2.append_stop("Station 2", WaitCondition(WaitConditionType.EMPTY_CARGO))

        blueprint.add_train_at_position(config, (0, 0), Direction.NORTH, schedule1)
        train1 = blueprint.find_train_from_wagon(blueprint.entities[-1])
        blueprint.add_train_at_position(config, (10, 0), Direction.NORTH, schedule1)
        train2 = blueprint.find_train_from_wagon(blueprint.entities[-1])
        blueprint.add_train_at_position(config, (20, 0), Direction.NORTH, schedule2)
        train3 = blueprint.find_train_from_wagon(blueprint.entities[-1])

        assert blueprint.to_dict()["blueprint"]["schedules"] == [
            {
                "locomotives": [1, 3],
                "schedule": [
                    {
                        "station": "Station 1",
                        "wait_conditions": [
                            {
                                "type": WaitConditionType.FULL_CARGO,
                                # "compare_type": "or", # Default
                            }
                        ],
                    }
                ],
            },
            {
                "locomotives": [5],
                "schedule": [
                    {
                        "station": "Station 2",
                        "wait_conditions": [
                            {
                                "type": WaitConditionType.EMPTY_CARGO,
                                # "compare_type": "or", # Default
                            }
                        ],
                    }
                ],
            },
        ]

        blueprint.remove_train(train2)
        assert len(blueprint.entities) == 4
        assert blueprint.to_dict()["blueprint"]["schedules"] == [
            {
                "locomotives": [1],
                "schedule": [
                    {
                        "station": "Station 1",
                        "wait_conditions": [
                            {
                                "type": WaitConditionType.FULL_CARGO,
                                # "compare_type": WaitConditionCompareType.OR, # Default
                            }
                        ],
                    }
                ],
            },
            {
                "locomotives": [3],
                "schedule": [
                    {
                        "station": "Station 2",
                        "wait_conditions": [
                            {
                                "type": WaitConditionType.EMPTY_CARGO,
                                # "compare_type": WaitConditionCompareType.OR, # Default
                            }
                        ],
                    }
                ],
            },
        ]

    # =========================================================================
    # Train Queries
    # =========================================================================

    def test_find_train_from_wagon(self):
        # 3 trains:
        # 1 going north, "1-FA"
        # 1 going around a east-to-north corner, dual-headed "1-C-1"
        # 1 isolated locomotive pointing west, "1"
        test_string = "0eNqVk9FuwyAMRf+F5xQ5BmLIr0zTlLasQqJQkaRbVOXfR9Mqm5R2yx5B9rn32nBhW9/bU3KhY/WFuV0MLatfLqx1h9D46103nCyrmevskRUsNMfrKTXOs7FgLuztJ6vL8bVgNnSuc/bWPx2Gt9AftzblgrnTx108xs6dbaadYptbYrjqZMwGJRVsYDUK5KbSpLJETC7DmlsZjMWCjSvZKHmFJRhB6i5CHEAYqHCpw0EbDSUprZBIKRIkQN4sLRyI2cG7791+89EcMuS3eGZ9PDnDd006xOdwNFyRLvGeTpacSqmleCDDS0IAFJCzA5ABCTmmkNNoXDjn0pgyJPTeP7CkVk5cEVfi25BY+ng4zmolXlQcDU6D/KcCzQpN6pz3Ng1/L01Wz5aWH//0Peofv6lgZ5vaqQB1KckgVQZBCxzHLxBxE5M="
        blueprint = Blueprint(test_string)

        # Grab train #1 with the locomotive
        assert blueprint.find_train_from_wagon(blueprint.entities[0]) == [
            blueprint.entities[0],
            blueprint.entities[2],
            blueprint.entities[6],
        ]

        # Grab dual headed from central cargo wagon
        assert blueprint.find_train_from_wagon(blueprint.entities[3]) == [
            blueprint.entities[1],
            blueprint.entities[3],
            blueprint.entities[5],
        ]

        # Isolated locomotive
        assert blueprint.find_train_from_wagon(blueprint.entities[4]) == [
            blueprint.entities[4]
        ]

        # Curved locomotive like above, with a fluid wagon within range of the
        # head but facing a perpendicular direction
        test_string = "0eNqNktFqwzAMRf9Fz5mRZTu28ytjjLT1iiGxi5N0KyX/PiUtZawZ7FFG99wrWVfYdVM4lZhGaK4Q9zkN0LxeYYjH1HbL23g5BWggjqGHClLbL1VpYwdzBTEdwhc0cn6rIKQxjjHc9GtxeU9TvwuFGx7KLu9zn8d4Dkw75YElOS0+jHkh0qImiV5ZU8EFGlJWICqPNRm2yyUyuL1JUKDzDqU1zpC1xlhlFeraWW59SkCPBB/dFA8vn+2RIRsRtLo5axIkV9Yv2w24esD3bTnmv+HkhbFO0n06LYWV2mm1YSOkJURSyLMjWo8aeUyl19XEdObWXBiSpq7biKT/uXFVC/Lkl63dM6nnKByPP3g9gebHxVRwDmVYe8hJbT3Z2hM6RfP8Da2auHA="
        blueprint = Blueprint(test_string)

        # Make sure the fluid wagon is not falsely included with the train
        assert blueprint.find_train_from_wagon(blueprint.entities[0]) == [
            blueprint.entities[0],
            blueprint.entities[2],
            blueprint.entities[3],
        ]

        # 1 train, "2-C" pointing east
        test_string = "0eNqVkk1uhDAMha9SeZ2pZgIIJrv2Cl1WCGUgpZFCgkJgilDuXgdoi1r6t7Mjv+85tie4qF60VmoHbAJZGt0Be5ygk7XmKry5sRXAQDrRAAHNm5BZLhV4AlJX4gXYyZNfJcqUpjFODmIjpD4nILSTTorFeE7GQvfNRVgkv+tLbmtzuPLaaIS2pkMNhmiHnAONKIERWHyMkG6sRA5fCo63aRIMB3wyFmt0r1Ro+JMV3Wt1x4km3zvRZAcc/RF8yn4E46S68llUvVpH9UELOSXRpmJZ4pseHpbo5g59r1y6Ahddze4LCkEtt6JYN2cs1q3xE04LfD5v+Avv/v880bRuDMA8/Gi+Eba5QgKDsN3sQrNTnJ5pmkbpOcli718BQnHlBA=="
        blueprint = Blueprint(test_string)

        # Grab from the cargo wagon (which is pointing the wrong way!)
        # and make sure the output is reversed so trains are at front
        assert blueprint.find_train_from_wagon(blueprint.entities[0]) == [
            blueprint.entities[2],
            blueprint.entities[1],
            blueprint.entities[0],
        ]

    def test_find_trains_filtered(self):
        # 3 trains:
        # 1 going north, "1-FA"
        # 1 going around a east-to-north corner, dual-headed "1-C-1"
        # 1 isolated locomotive pointing west, "1"
        test_string = "0eNqVk9FuwyAMRf+F5xQ5BmLIr0zTlLasQqJQkaRbVOXfR9Mqm5R2yx5B9rn32nBhW9/bU3KhY/WFuV0MLatfLqx1h9D46103nCyrmevskRUsNMfrKTXOs7FgLuztJ6vL8bVgNnSuc/bWPx2Gt9AftzblgrnTx108xs6dbaadYptbYrjqZMwGJRVsYDUK5KbSpLJETC7DmlsZjMWCjSvZKHmFJRhB6i5CHEAYqHCpw0EbDSUprZBIKRIkQN4sLRyI2cG7791+89EcMuS3eGZ9PDnDd006xOdwNFyRLvGeTpacSqmleCDDS0IAFJCzA5ABCTmmkNNoXDjn0pgyJPTeP7CkVk5cEVfi25BY+ng4zmolXlQcDU6D/KcCzQpN6pz3Ng1/L01Wz5aWH//0Peofv6lgZ5vaqQB1KckgVQZBCxzHLxBxE5M="

        blueprint = Blueprint(test_string)

        # Return all trains:
        assert blueprint.find_trains_filtered() == [
            [blueprint.entities[0], blueprint.entities[2], blueprint.entities[6]],
            [blueprint.entities[1], blueprint.entities[3], blueprint.entities[5]],
            [blueprint.entities[4]],
        ]

        # Invert selection (return no trains)
        assert blueprint.find_trains_filtered(invert=True) == []

        # Test train length (int)
        assert blueprint.find_trains_filtered(train_length=3) == [
            [blueprint.entities[0], blueprint.entities[2], blueprint.entities[6]],
            [blueprint.entities[1], blueprint.entities[3], blueprint.entities[5]],
        ]

        # Test train length (range)
        assert blueprint.find_trains_filtered(train_length=(None, None)) == [
            [blueprint.entities[0], blueprint.entities[2], blueprint.entities[6]],
            [blueprint.entities[1], blueprint.entities[3], blueprint.entities[5]],
            [blueprint.entities[4]],
        ]

        # Test num-type
        assert blueprint.find_trains_filtered(
            num_type={"locomotive": 2, "cargo-wagon": 1}
        ) == [[blueprint.entities[1], blueprint.entities[3], blueprint.entities[5]]]

        # Test orientation
        assert blueprint.find_trains_filtered(orientation=Orientation.WEST) == [
            [blueprint.entities[4]]
        ]

        # Test config
        config = TrainConfiguration("1-FA")
        assert blueprint.find_trains_filtered(config=config) == [
            [blueprint.entities[0], blueprint.entities[2], blueprint.entities[6]]
        ]

        # Test limit
        assert blueprint.find_trains_filtered(limit=1) == [
            [blueprint.entities[0], blueprint.entities[2], blueprint.entities[6]]
        ]

        # Test continuity around corners
        test_string = "0eNqNkutqwzAMhd9Fv1PjayTnVcYYaWeKIbFLLt1KybtPSdoyaKD9KXHO0SehK+ybMZy6mAaorhAPOfVQfVyhj8dUN3NvuJwCVBCH0EIBqW7nqqtjA1MBMX2HX6jU9FlASEMcYlj9S3H5SmO7Dx0LHs4mH3Kbh3gOnHbKPVtymudwzE6XvoALVNoogY7zcxc5qV41UnDrKVo/og91d8y7n/rI4s1sISWS0u42g7ZnsAiRVcaRI+Ws9iWhm3c9sy537E1j02ygmHdRUApSpZXlncU6of06aIPIO2+kMeilIzJIfjW+BrJvAzlBVKJaFl2AvCBU0pstoJKviMobPikytLLa3e76Gsm9+QmkRWnJmjuQU88czMZ/t3xm9e+RCziHrl80mpRFrxH5eI7sNP0BD83n6g=="
        blueprint = Blueprint(test_string)

        assert blueprint.find_trains_filtered() == [
            [
                blueprint.entities[4],
                blueprint.entities[3],
                blueprint.entities[2],
                blueprint.entities[1],
                blueprint.entities[0],
            ]
        ]

        # A whole bunch of trains in some hypothetical depot
        test_string = """0eNqdmUtz2jAUhf9KR2uTsV6Wza5ddNVdlx0m44BCNDUyY0xSJsN/r4xJoI3DnHt3tpE/Pe6951joVTw0e7/tQuzF/FWEZRt3Yv7rVezCOtbN8Kw/bL2Yi9D7jchErDfDXVeHRhwzEeLK/xFzeVxkwsc+9MGP759uDvdxv3nwXWrw/uauT++un/rZCZGJbbtLb7Vx6CqRZsqktgcx15VM/FXo/HL8WR2zD1iFY3WFYzUB63CsIWAtjrUErMaxBQFLCJnDsYoQspKAJYSsImAJIZM5gUuImbzUWdMu203bh2c/BZXlFbTtQuLUY4P8TtkpMqHUFCEdJKHWJCEfJKHYJCEhJKHaJCUjLuU2YONs17fbm1D9HzRLAzrHUPyof/sv35tDjGKqLwf29S7F9t++iuu+fo5XX75NdlWCCanfEtJ9TEg3mZAVw1IcYCk5w1MQrmSYCsJVDFdBuJfCXNbdup291OvU9pb6T4Zu+EZ4To/aLrWJ+6aZ6sswLAyZg2V4GMItGCaGcB1YLcOCfbbkk/KtOP6IjJhjkABXcwwS4UqGjSFcxbAxhKsZNoZwDcPGEK4lq7LJNcAtyKqMcR1ZlTFuCaunuqKy1FNXZAeA5mBysipjXElWZYyryKqMcTWqyvbzUE6qsjFkVcZGbMmqjHELsipjXEfbthBWuCTrPTbiiqz3ENfmZL3HuJKs9xhX0bYtJrc3ti1vW4mvU1sJqxnWUgFTMAxrQbiXIqy7PjSN7w43bMDclUY7e8VH8tsWDP9CBu8YnoJwS4anINxLPT42+7D6fKGVYy10kTNMCxh4IRmmhXAVw1oQrmZYC8I1qMnmvPhZhnUh4y4YBoNwHcNgEG7JMBiEWzEM5gN3kdxg+eRX++Z8jHDJheE+fYkZd9VmPKmYsI9MvNShv1+2cXXqeoQl1Lbu/P35RKPtUrvz9WP6tBbHxTCxqX+2yDy/2faHAbgY5nQ6O5lfHbVk4tl3u3HSpTSuUs5pV9nSHI9/Ad/ZT18="""
        bp = Blueprint(test_string)

        # All trains
        trains = bp.find_trains_filtered()
        assert len(trains) == 4

        # Trains with length of 3
        trains = bp.find_trains_filtered(train_length=3)
        assert len(trains) == 3

        # Trains facing east
        trains = bp.find_trains_filtered(orientation=Orientation.EAST)
        assert len(trains) == 2

        # Trains not facing east
        trains = bp.find_trains_filtered(orientation=Orientation.EAST, invert=True)
        assert len(trains) == 2

        # Trains at stations
        trains = bp.find_trains_filtered(at_station=True)
        assert len(trains) == 3

        # Trains not at stations
        trains = bp.find_trains_filtered(at_station=True, invert=True)
        assert len(trains) == 1

        # Trains at stations with the name "Station A"
        trains = bp.find_trains_filtered(at_station="Station A")
        assert len(trains) == 1

        # Trains at stations with the name "Station A" or "Station B"
        trains = bp.find_trains_filtered(at_station={"Station A", "Station B"})
        assert len(trains) == 2

        # Trains with 2 locomotives and 1 cargo wagon
        trains = bp.find_trains_filtered(num_type={"locomotive": 2, "cargo-wagon": 1})
        assert len(trains) == 2

        # Trains with 2 "locomotive"s and 1 "cargo-wagon"
        trains = bp.find_trains_filtered(num_name={"locomotive": 2, "cargo-wagon": 1})
        assert len(trains) == 2

        # Trains with 2 locomotives followed by 1 cargo wagon
        config = TrainConfiguration("2-1")
        trains = bp.find_trains_filtered(config=config)
        assert len(trains) == 1

        # Trains that follow a specific schedule
        schedule = Schedule()
        schedule.append_stop("Station A", WaitCondition(WaitConditionType.FULL_CARGO))
        schedule.append_stop("Station B", WaitCondition(WaitConditionType.EMPTY_CARGO))
        trains = bp.find_trains_filtered(schedule=schedule)
        assert schedule.stops == bp.schedules[0].stops
        assert len(trains) == 1

        # Trains that follow a different schedule
        schedule = Schedule()
        trains = bp.find_trains_filtered(schedule=schedule)
        assert len(trains) == 0

    # =========================================================================
    # TileCollection
    # =========================================================================

    def test_find_tile(self):
        blueprint = Blueprint()
        blueprint.tiles.append("refined-concrete", position=(0, 0))
        blueprint.tiles.append("landfill", position=(10, 10))

        assert blueprint.find_tile((0, 0)) is blueprint.tiles[0]
        assert blueprint.find_tile((10, 10)) is blueprint.tiles[1]
        with pytest.raises(AttributeError):
            blueprint.find_tile((5, 5)).position = (15, 15)

    # =========================================================================

    def test_find_tiles_filtered(self):
        blueprint = Blueprint()
        blueprint.tiles.append("refined-concrete", position=(0, 0))
        blueprint.tiles.append("landfill", position=(10, 10))

        # No criteria
        result = blueprint.find_tiles_filtered()
        assert result == blueprint.tiles._root

        # Position and radius
        result = blueprint.find_tiles_filtered(position=(0, 0), radius=5)
        assert result == [blueprint.tiles[0]]

        # Area (long)
        result = blueprint.find_tiles_filtered(area=AABB(0, 0, 11, 11))
        assert result == blueprint.tiles._root

        # Area (short)
        result = blueprint.find_tiles_filtered(area=[0, 0, 11, 11])
        assert result == blueprint.tiles._root

        # Name
        result = blueprint.find_tiles_filtered(name="refined-concrete")
        assert result == [blueprint.tiles[0]]

        # Names
        result = blueprint.find_tiles_filtered(name={"refined-concrete", "landfill"})
        assert result == blueprint.tiles._root

        result = blueprint.find_tiles_filtered(name="refined-concrete", invert=True)
        assert result == [blueprint.tiles[1]]

    # =========================================================================
    # Transformable
    # =========================================================================

    def test_translate(self):
        blueprint = Blueprint()
        blueprint.entities.append("wooden-chest", tile_position=(10, 10))
        blueprint.tiles.append("refined-concrete", position=(1, 1))

        blueprint.translate(-5, -5)

        assert blueprint.entities[0].tile_position == Vector(5, 5)
        assert blueprint.tiles[0].position == Vector(-4, -4)

        blueprint.entities.append("straight-rail")
        assert blueprint.double_grid_aligned == True

        with pytest.warns(GridAlignmentWarning):
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

        assert blueprint.entities[0].tile_position == Vector(-1, 0)
        assert blueprint.entities[1].tile_position == Vector(-5, 4)
        assert blueprint.entities[2].tile_position == Vector(-3, 1)
        assert blueprint.entities[2].direction == 2
        assert blueprint.tiles[0].position == Vector(-5, 0)
        assert blueprint.tiles[1].position == Vector(-1, 4)

        with pytest.raises(RotationError):
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

        assert blueprint.entities[0].tile_position == Vector(-1, 0)
        assert blueprint.entities[1].tile_position == Vector(-5, 4)
        assert blueprint.entities[2].tile_position == Vector(-4, 1)
        assert blueprint.entities[2].direction == 0
        assert blueprint.tiles[0].position == Vector(-1, 4)
        assert blueprint.tiles[1].position == Vector(-5, 0)

        blueprint.flip("vertical")

        assert blueprint.entities[0].tile_position == Vector(-1, -1)
        assert blueprint.entities[1].tile_position == Vector(-5, -5)
        assert blueprint.entities[2].tile_position == Vector(-4, -3)
        assert blueprint.entities[2].direction == 4
        assert blueprint.tiles[0].position == Vector(-1, -5)
        assert blueprint.tiles[1].position == Vector(-5, -1)

        with pytest.raises(ValueError):
            blueprint.flip("incorrectly")
        with pytest.raises(FlippingError):
            blueprint.entities.append("chemical-plant", tile_position=(4, 4))
            blueprint.flip()

    # =========================================================================

    def test_eq(self):
        blueprint1 = Blueprint()

        # Trivial case
        assert blueprint1 == blueprint1

        blueprint2 = Blueprint()

        assert blueprint1 == blueprint2

        blueprint2.label = "some label"

        assert blueprint1 != blueprint2

        # Non-blueprint
        entity = Container("wooden-chest")

        assert blueprint1 != entity

    def test_json_schema(self):
        Blueprint.json_schema()

    def test_unreasonable_size(self):
        blueprint = Blueprint()

        blueprint.entities.append("transport-belt")
        blueprint.entities.append("transport-belt", tile_position=(15000, 0))
        with pytest.raises(UnreasonablySizedBlueprintError):
            blueprint.validate().reissue_all()

        blueprint.entities.clear()

        # TODO: reimplement
        blueprint.tiles.append("landfill")
        blueprint.tiles.append("landfill", position=(15000, 0))
        with pytest.raises(UnreasonablySizedBlueprintError):
            blueprint.validate().reissue_all()
