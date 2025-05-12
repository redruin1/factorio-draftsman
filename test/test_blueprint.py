# blueprint.py

from draftsman._factorio_version import __factorio_version__, __factorio_version_info__
from draftsman.blueprintable import Blueprint, get_blueprintable_from_string
from draftsman.classes.association import Association
from draftsman.classes.blueprint import TileList
from draftsman.classes.collision_set import CollisionSet
from draftsman.classes.entity_like import EntityLike
from draftsman.classes.entity_list import EntityList
from draftsman.classes.exportable import ValidationResult
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
from draftsman.tile import Tile, new_tile
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
    UnknownSignalWarning,
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

        broken_example = {"blueprint": {"item": "blueprint", "version": "incorrect"}}

        blueprint = Blueprint(broken_example, validate="none")
        assert blueprint.to_dict() == broken_example

        with pytest.raises(DataFormatError):
            blueprint.validate().reissue_all()

        # Valid format, but incorrect type
        with pytest.raises(IncorrectBlueprintTypeError):
            blueprint = Blueprint(
                "0eNqrVkrKKU0tKMrMK4lPys/PVrKqVsosSc1VskJI6IIldJQSk0syy1LjM/NSUiuUrAx0lMpSi4oz8/OUrIwsDE3MLY3MTSxNTcxNjWtrAVWjHQY="
            )

        # Invalid format
        with pytest.raises(MalformedBlueprintStringError):
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
        blueprint.version = (1, 1, 54, 0)
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
        blueprint.version = (1, 1, 54, 0)

        # Valid 3 args list
        # Test for floating point conversion error by using 0.1
        blueprint.label_color = (0.5, 0.1, 0.5)
        assert blueprint.label_color == Color(**{"r": 0.5, "g": 0.1, "b": 0.5})
        assert blueprint.to_dict()["blueprint"] == {
            "item": "blueprint",
            "label_color": {"r": 0.5, "g": 0.1, "b": 0.5},
            "version": encode_version(1, 1, 54, 0),
        }

        # Valid 4 args list
        blueprint.label_color = (1.0, 1.0, 1.0, 0.25)
        assert blueprint.to_dict()["blueprint"] == {
            "item": "blueprint",
            "label_color": {"r": 1.0, "g": 1.0, "b": 1.0, "a": 0.25},
            "version": encode_version(1, 1, 54, 0),
        }
        # Valid 3 args dict
        blueprint.label_color = {"r": 255, "g": 255, "b": 255}
        assert blueprint.to_dict()["blueprint"] == {
            "item": "blueprint",
            "label_color": {"r": 255, "g": 255, "b": 255},
            "version": encode_version(1, 1, 54, 0),
        }

        blueprint.label_color = {"r": 100, "g": 100, "b": 100, "a": 200}
        assert blueprint.to_dict()["blueprint"] == {
            "item": "blueprint",
            "label_color": {"r": 100, "g": 100, "b": 100, "a": 200},
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
            blueprint.label_color = "wrong"

        # Turn off validation
        blueprint.validate_assignment = "none"
        assert blueprint.validate_assignment is ValidationMode.NONE

        # Incorrect Data now works
        blueprint.label_color = "wrong"
        assert blueprint.label_color == "wrong"
        assert blueprint.to_dict()["blueprint"] == {
            "item": "blueprint",
            "label_color": "wrong",
            "version": encode_version(1, 1, 54, 0),
        }

        # We can set label color to anything
        blueprint.label_color = ("red", blueprint, 5)
        # But we can't always serialize it
        blueprint.to_dict()

    # =========================================================================

    def test_set_icons(self):
        blueprint = Blueprint()
        # Single Icon
        blueprint.icons = ["signal-A"]
        assert blueprint.icons == [
            Icon(**{"signal": {"name": "signal-A", "type": "virtual"}, "index": 1})
        ]
        assert blueprint["blueprint"]["icons"] == [
            Icon(**{"signal": {"name": "signal-A", "type": "virtual"}, "index": 1})
        ]
        # Multiple Icon
        blueprint.icons = ("signal-A", "signal-B", "signal-C")
        assert blueprint["blueprint"]["icons"] == [
            Icon(**{"signal": {"name": "signal-A", "type": "virtual"}, "index": 1}),
            Icon(**{"signal": {"name": "signal-B", "type": "virtual"}, "index": 2}),
            Icon(**{"signal": {"name": "signal-C", "type": "virtual"}, "index": 3}),
        ]

        # Raw signal dicts:

        blueprint.icons = [{"signal": "signal-A", "index": 2}]
        assert blueprint["blueprint"]["icons"] == [
            Icon(**{"signal": {"name": "signal-A", "type": "virtual"}, "index": 2})
        ]

        # Unrecognized dict
        with pytest.warns(UnknownSignalWarning):
            blueprint.icons = [
                {"signal": {"name": "some-signal", "type": "item"}, "index": 1}
            ]
        assert blueprint["blueprint"]["icons"] == [
            Icon(**{"signal": {"name": "some-signal", "type": "item"}, "index": 1})
        ]

        # None
        blueprint.icons = None
        assert blueprint.icons == None
        assert blueprint.to_dict()["blueprint"] == {
            "item": "blueprint",
            "version": encode_version(*__factorio_version_info__),
        }

        # Incorrect Signal Name
        with pytest.raises(DataFormatError):
            blueprint.icons = ["wrong!"]

        # Incorrect Signal dict format
        with pytest.raises(DataFormatError):
            blueprint.icons = {"incorrectly": "formatted"}

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

    def test_version(self):
        blueprint = Blueprint()

        blueprint.version = 1000
        assert blueprint.version == 1000

        blueprint.version = (1, 0, 40, 0)
        assert blueprint.version == 281474979332096

        blueprint.version = None
        assert blueprint.version == None
        assert blueprint.to_dict()["blueprint"] == {"item": "blueprint"}

        blueprint.validate_assignment = "none"
        blueprint.version = "wrong"
        assert blueprint.version == "wrong"
        assert blueprint.to_dict()["blueprint"] == {
            "item": "blueprint",
            "version": "wrong",
        }

        with pytest.raises(DataFormatError):
            blueprint.validate_assignment = "strict"
            blueprint.version = "wrong"

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
        assert len(blueprint.entities) == 1

        blueprint.entities = None
        assert isinstance(blueprint.entities, EntityList)
        assert blueprint.entities._root == []

        # Set by EntityList
        blueprint.entities.append("wooden-chest")
        blueprint.entities.append("wooden-chest", tile_position=(1, 0))
        blueprint.add_circuit_connection("red", 0, 1)
        blueprint2 = Blueprint()
        blueprint2.entities = blueprint.entities
        assert isinstance(blueprint.entities, EntityList)
        assert isinstance(blueprint2.entities, EntityList)
        assert blueprint.entities is not blueprint2.entities

        # Set by list of dict
        blueprint.entities = [{"name": "wooden-chest", "position": (0.5, 0.5)}]
        assert isinstance(blueprint.entities, EntityList)
        assert len(blueprint.entities) == 1
        assert blueprint.entities[-1].name == "wooden-chest"
        assert blueprint.entities[-1].position.to_dict() == {"x": 0.5, "y": 0.5}

        # Set individual as Entity
        blueprint.entities[-1] = Container("steel-chest")
        assert len(blueprint.entities) == 1
        assert blueprint.entities[-1].name == "steel-chest"
        assert blueprint.entities[-1].position.to_dict() == {"x": 0.5, "y": 0.5}

        # Set individual as dict
        blueprint.entities[-1] = {"name": "steel-chest", "position": (0.5, 0.5)}
        assert len(blueprint.entities) == 1
        assert blueprint.entities[-1].name == "steel-chest"
        assert blueprint.entities[-1].position.to_dict() == {"x": 0.5, "y": 0.5}

        # Warn unknown entity (list)
        blueprint.validate_assignment = "none"
        blueprint.entities = [new_entity("undocumented-entity")]  # No warning
        with pytest.warns(UnknownEntityWarning):
            blueprint.validate_assignment = "strict"
            blueprint.entities = [new_entity("undocumented-entity")]
            blueprint.validate().reissue_all()  # Warning

        # Warn unknown entity (individual)
        blueprint.entities.validate_assignment = "none"
        blueprint.entities[-1] = new_entity("undocumented-entity")  # No warning
        with pytest.warns(UnknownEntityWarning):
            blueprint.validate_assignment = "strict"
            blueprint.entities[-1] = new_entity("undocumented-entity")
            blueprint.validate().reissue_all()  # Warning

        # Format error
        with pytest.raises(TypeError):
            blueprint.entities = "wrong"

    # =========================================================================

    def test_set_tiles(self):
        blueprint = Blueprint()
        blueprint.tiles = [Tile("refined-concrete")]
        assert isinstance(blueprint.tiles, TileList)

        blueprint.tiles = None
        assert isinstance(blueprint.tiles, TileList)
        assert blueprint.tiles._root == []

        # Set by TileList
        blueprint.tiles.append("landfill")
        blueprint2 = Blueprint()
        blueprint2.tiles = blueprint.tiles
        assert isinstance(blueprint.tiles, TileList)
        assert isinstance(blueprint2.tiles, TileList)
        assert blueprint.tiles is not blueprint2.tiles
        assert blueprint.tiles[0].parent is blueprint
        assert blueprint2.tiles[0].parent is not blueprint

        # Set by list of dict
        blueprint.tiles = [{"name": "landfill", "position": (0, 0)}]
        assert isinstance(blueprint.tiles, TileList)
        assert len(blueprint.tiles) == 1
        assert isinstance(blueprint.tiles[-1], Tile)
        assert blueprint.tiles[-1].name == "landfill"
        assert blueprint.tiles[-1].position.to_dict() == {"x": 0, "y": 0}

        # Set individual as Entity
        blueprint.tiles[-1] = Tile("landfill")
        assert len(blueprint.tiles) == 1
        assert blueprint.tiles[-1].name == "landfill"
        assert blueprint.tiles[-1].position.to_dict() == {"x": 0, "y": 0}

        # Set individual as dict
        # TODO: is this desirable?
        # blueprint.tiles[-1] = {"name": "landfill", "position": (1, 1)}
        # assert len(blueprint.tiles) == 1
        # assert isinstance(blueprint.tiles[-1], Tile)
        # assert blueprint.tiles[-1].name == "landfill"
        # assert blueprint.tiles[-1].position.to_dict() == {"x": 1, "y": 1}

        # Warn unknown entity (list)
        blueprint.tiles.validate_assignment = "none"
        blueprint.tiles = [new_tile("undocumented-tile")]  # No warning
        with pytest.warns(UnknownTileWarning):
            blueprint.tiles.validate_assignment = "strict"
            blueprint.tiles = [new_tile("undocumented-tile")]
            blueprint.tiles.validate().reissue_all()  # Warning

        # Warn unknown entity (individual)
        blueprint.tiles.validate_assignment = "minimum"
        blueprint.tiles[-1] = new_tile("undocumented-tile")  # No warning
        with pytest.warns(UnknownTileWarning):
            blueprint.tiles.validate_assignment = "strict"
            blueprint.tiles[-1] = new_tile("undocumented-tile")
            # blueprint.validate().reissue_all() # Warning

        # Format error
        with pytest.raises(DataFormatError):
            blueprint.tiles = "wrong"

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
                    "schedule": {
                        "records": [
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
                    },
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
        blueprint.version = (1, 1, 54, 0)

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
        blueprint.version = 0
        assert blueprint.version_tuple() == (0, 0, 0, 0)

    # =========================================================================

    def test_version_string(self):
        blueprint = Blueprint()
        assert blueprint.version_string() == __factorio_version__
        blueprint.version = (0, 0, 0, 0)
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
        blueprint.add_power_connection("a", "b", side_1="input")
        blueprint.tiles.append("landfill")
        blueprint.snapping_grid_position = (-1, -1)  # also test this
        self.maxDiff = None
        assert blueprint.to_dict()["blueprint"] == {
            "item": "blueprint",
            "entities": [
                {
                    "name": "power-switch",
                    "position": {"x": 2.0, "y": 2.0},
                    "entity_number": 1,
                },
                {
                    "name": "small-electric-pole",
                    "position": {"x": 6.5, "y": 1.5},
                    "entity_number": 2,
                },
            ],
            "wires": [[1, 5, 2, 5]],
            "tiles": [{"name": "landfill", "position": {"x": 1, "y": 1}}],
            "version": encode_version(*__factorio_version_info__),
        }

        # Non-string id connection case
        example_string = "0eNqVkMFugzAQRP9lz0uETUyAX4lQROi2XckYZDuhEfK/dwFVPTRS1Is1tmbermeBq73R5NlFaBbgfnQBmvMCgT9cZ9c31w0EDUzjTD4LM8f+ExICuzf6gkalFoFc5Mi0J7fL4+Juw5W8GPCHEIbO2ows9dFzn02jJUDhBsmObh0lvGNeHAzCQ4Kn6mBSwj9E/U+iyl8RC3z6yyfLVTuoyqWB3XUJsYsSfe9soLWMmf3WxFmhQo2qRVFGlBElJxZYtuLjSINM/O0f4U4+bNNMqetjXRujTVloldI3iaSImA=="
        blueprint.load_from_string(example_string)
        assert blueprint.to_dict()["blueprint"] == {
            "item": "blueprint",
            "icons": [{"index": 1, "signal": {"name": "power-switch"}}],
            "entities": [
                {
                    "name": "small-electric-pole",
                    "position": {"x": 403.5, "y": 178.5},
                    "entity_number": 1,
                },
                {
                    "name": "small-electric-pole",
                    "position": {"x": 410.5, "y": 178.5},
                    "entity_number": 2,
                },
                {
                    "name": "power-switch",
                    "position": {"x": 408.0, "y": 180.0},
                    # "switch_state": False, # Default
                    "entity_number": 3,
                },
            ],
            "wires": [[1, 1, 2, 1], [1, 5, 2, 5], [2, 5, 3, 6]],
            "version": encode_version(2, 0, 28, 1),
        }

        # Numeric Locomotive case
        bp_string = "0eNqVk92OgjAQhV/FzHU1iKDC7V7uE2w2hlSYhYnQkrbqEsO77xT8izEbDTedduY7Z+j0BNt6j60h5SA9AeVaWUi/T2CpVLL2e0o2CCkYSTX0AkgV+AvpvBdPkmqd60Y7OuBdathvBKBy5AhH+BB0mdo3WzTMEtd6LGXeTa1jtbJy00FUQKstF2vllRgYBbGAjuvWK1YpyGA+nkbe1AM8fBu+eh2+EE86f4Jc3yFRyW2NWa1Lso5ymx0r4rjRB1IlpD+ytihAG2ItOVKCWRg/UY/ebi15vbX4Xfh8/jp8eYV7qGK2bv9DJg9IAfbybwD8eNm8wmJfn+frdhk+XtydezJjtCnOY37FfBj03Wk1+ZxNvqTKK2nY0lGSy/hVFIOxsYjhrTSYua71LWifd147avwA8L3urDceBP2Gv8Gi0/nOo9TYxsUA7/Ig+Qxy2DDj9iIFHNDYwV+8DJMoSeI4jJeLcN73fwrmQGw="
        blueprint.load_from_string(bp_string)  # TODO
        # assert blueprint.to_dict()["blueprint"] == {
        #     "icons": [
        #         {"signal": {"type": "item", "name": "rail"}, "index": 1},
        #         {"signal": {"type": "item", "name": "locomotive"}, "index": 2},
        #     ],
        #     "entities": [
        #         {
        #             "entity_number": 1,
        #             "name": "locomotive",
        #             "position": {"x": 116, "y": -57},
        #             "orientation": 0.25,
        #         },
        #         {
        #             "entity_number": 2,
        #             "name": "straight-rail",
        #             "position": {"x": 113, "y": -57},
        #             "direction": 2,
        #         },
        #         {
        #             "entity_number": 3,
        #             "name": "straight-rail",
        #             "position": {"x": 115, "y": -57},
        #             "direction": 2,
        #         },
        #         {
        #             "entity_number": 4,
        #             "name": "straight-rail",
        #             "position": {"x": 117, "y": -57},
        #             "direction": 2,
        #         },
        #         {
        #             "entity_number": 5,
        #             "name": "straight-rail",
        #             "position": {"x": 119, "y": -57},
        #             "direction": 2,
        #         },
        #         {
        #             "entity_number": 6,
        #             "name": "train-stop",
        #             "position": {"x": 119, "y": -55},
        #             "direction": 2,
        #             "station": "Creighton K. Yanchar",
        #         },
        #     ],
        #     "schedules": [
        #         {
        #             "locomotives": [1],
        #             "schedule": [
        #                 {
        #                     "station": "Creighton K. Yanchar",
        #                     "wait_conditions": [
        #                         {
        #                             # "compare_type": "or",
        #                             "type": "time",
        #                             "ticks": 1800,
        #                         }
        #                     ],
        #                 }
        #             ],
        #         }
        #     ],
        #     "item": "blueprint",
        #     "version": 281479275151360,
        # }

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

            def validate(self, mode):
                return ValidationResult([], [])

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
                    "entity_number": 1,
                },
                {
                    "name": "small-electric-pole",
                    "position": {"x": 0.5, "y": 1.5},
                    "entity_number": 2,
                },
                {
                    "name": "small-electric-pole",
                    "position": {"x": 5.5, "y": 1.5},
                    "entity_number": 3,
                },
            ],
            "wires": [[1, 2, 2, 2], [2, 1, 3, 1], [2, 5, 3, 5]],
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
                    "entity_number": 1,
                },
                {
                    "name": "small-electric-pole",
                    "position": {"x": 0.5, "y": 1.5},
                    "entity_number": 2,
                },
                {
                    "name": "small-electric-pole",
                    "position": {"x": 5.5, "y": 1.5},
                    "entity_number": 3,
                },
            ],
            "wires": [[1, 2, 2, 2], [2, 1, 3, 1], [2, 5, 3, 5]],
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
                    "entity_number": 1,
                },
                {
                    "name": "substation",
                    "position": {"x": 7.0, "y": 1.0},
                    "entity_number": 2,
                },
            ],
            "wires": [[1, 5, 2, 5]],
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
                    "entity_number": 1,
                },
                {
                    "name": "substation",
                    "position": {"x": 7.0, "y": 1.0},
                    "entity_number": 2,
                },
            ],
            "wires": [[1, 5, 2, 5]],
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
        # 1.0
        # with pytest.warns(TooManyConnectionsWarning):
        #     blueprint.add_power_connection(0, 6)
        # with pytest.warns(TooManyConnectionsWarning):
        #     blueprint.add_power_connection(6, 0)

    # =========================================================================

    def test_remove_power_connections(self):
        blueprint = Blueprint()

        blueprint.entities.append("transport-belt")
        blueprint.entities.append("small-electric-pole", tile_position=(1, 0))
        blueprint.entities.append("small-electric-pole", tile_position=(2, 0))
        blueprint.entities.append("power-switch", tile_position=(0, 1))
        blueprint.entities.append("radar", tile_position=(0, 3))

        blueprint.add_power_connection(1, 2)
        blueprint.add_power_connection(3, 1, side_1="input")
        blueprint.add_power_connection(3, 2, side_1="output")
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
                "wires": [[2, 5, 3, 5], [4, 5, 2, 5], [4, 6, 3, 5]],
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
            "wires": [[3, 5, 2, 5], [1, 5, 2, 5]],
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
                "wires": [
                    [1, 5, 4, 5],
                    [1, 5, 5, 5],
                    [1, 5, 3, 5],
                    [1, 5, 2, 5],
                    [2, 5, 3, 5],
                    [2, 5, 5, 5],
                    [2, 5, 4, 5],
                    [2, 5, 1, 5],
                    [3, 5, 2, 5],
                    [3, 5, 5, 5],
                    [3, 5, 4, 5],
                    [3, 5, 1, 5],
                    [4, 5, 1, 5],
                    [4, 5, 5, 5],
                    [4, 5, 3, 5],
                    [4, 5, 2, 5],
                    [5, 5, 4, 5],
                    [5, 5, 3, 5],
                    [5, 5, 2, 5],
                    [5, 5, 1, 5],
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
                "wires": [
                    [1, 5, 3, 5],
                    [1, 5, 2, 5],
                    [2, 5, 4, 5],
                    [2, 5, 1, 5],
                    [3, 5, 4, 5],
                    [3, 5, 1, 5],
                    [4, 5, 3, 5],
                    [4, 5, 2, 5],
                ],
                "version": encode_version(*__factorio_version_info__),
            }
        }
        # Test prefer_axis
        # blueprint.entities = None
        # blueprint.entities.append("medium-electric-pole")
        # blueprint.entities.append("medium-electric-pole", tile_position=(5, 0))
        # blueprint.entities.append("medium-electric-pole", tile_position=(1, 1))
        # blueprint.generate_power_connections(prefer_axis=False)
        # assert blueprint.to_dict() == {
        #     "blueprint": {
        #         "item": "blueprint",
        #         "entities": [
        #             {
        #                 "name": "medium-electric-pole",
        #                 "position": {"x": 0.5, "y": 0.5},
        #                 "neighbours": [2, 3],
        #                 "entity_number": 1,
        #             },
        #             {
        #                 "name": "medium-electric-pole",
        #                 "position": {"x": 5.5, "y": 0.5},
        #                 "neighbours": [1, 3],
        #                 "entity_number": 2,
        #             },
        #             {
        #                 "name": "medium-electric-pole",
        #                 "position": {"x": 1.5, "y": 1.5},
        #                 "neighbours": [1, 2],
        #                 "entity_number": 3,
        #             },
        #         ],
        #         "version": encode_version(*__factorio_version_info__),
        #     }
        # }

        # Test too many power connections
        # blueprint.entities = None
        # for i in range(3):
        #     blueprint.entities.append("medium-electric-pole", tile_position=(0, i))
        #     blueprint.entities.append("medium-electric-pole", tile_position=(3, i))
        # blueprint.generate_power_connections()

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
                    "entity_number": 1,
                },
                {
                    "name": "substation",
                    "position": {"x": 7.0, "y": 1.0},
                    "entity_number": 2,
                },
            ],
            "wires": [[1, 1, 2, 1]],
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
                    "entity_number": 1,
                },
                {
                    "name": "substation",
                    "position": {"x": 7.0, "y": 1.0},
                    "entity_number": 2,
                },
            ],
            "wires": [[1, 2, 2, 2]],
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
        blueprint.entities.append("lightning-attractor", tile_position=(0, 6), id="3")

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
        blueprint.add_circuit_connection(
            "green", "a", "b", side_1="input", side_2="output"
        )
        self.maxDiff = None
        actual = blueprint.to_dict()
        expected = {
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
                "wires": [[2, 1, 3, 1], [2, 2, 3, 4]],
                "version": encode_version(*__factorio_version_info__),
            }
        }
        import difflib
        import pprint
        if actual != expected:
            actual_str = pprint.pformat(actual, width=120)
            expected_str = pprint.pformat(expected, width=120)
            diff = difflib.unified_diff(
                expected_str.splitlines(), actual_str.splitlines(),
                fromfile='expected', tofile='actual', lineterm=''
            )
            print('\n'.join(diff))
        assert actual == expected
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
            "wires": [[3, 2, 2, 2], [1, 1, 2, 1]],
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
                    "schedule": {
                        "records": [
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
                "schedule": {
                    "records": [
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
                "schedule": {
                    "records": [
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
            },
            {
                "locomotives": [7],
                "schedule": {
                    "records": [
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
                    "schedule": {
                        "records": [
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
                "schedule": {
                    "records": [
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
                "schedule": {
                    "records": [
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
            },
            {
                "locomotives": [11],
                "schedule": {
                    "records": [
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
        test_string = "0eNq1lM1ugzAQhN9lz1ZU/tLCuYcee24VIQMLsWpsZJukKOLdaxuS0CqHoLY3e7T+dtYa+wQF77FTTBjITsBKKTRk7yfQrBGUO03QFiEDRRmHkQATFX5CFozkRhGXpWylYQdclIbjjgAKwwzDCe43Qy76tkBlWeTGeQKd1PaIFI5vMXEcERgsLgg2cfSYjA5KC445lw3ThpU6P+6Z3bfywEQDWU25RgJSMduQTqiHTeKc/3AQ3ukg/TcH0co7ePpzB/HKO/itAxsKXe6x6vmcimtbtw9ItKhw3RWWUlVzPM8keEFaWZtHykxu01t5s1ORxXVUYW6Gzo0lla2b13XPbZp3PsQX1LOSnazr9TRsOzM43G50xO+DhCS+a5BXyg+o3tZ376jWKBpUeafQrszsxHU1svxwKIHlleVV/+xqJd3Dj6Z78Gp4UeOFamNXUH9oIcZn0b9wZrC1bq7/CQE7j/bDJdswjdM0ScJkG4XBOH4Bm4OGxA=="
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
                "schedule": {
                    "records": [
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
            },
            {
                "locomotives": [5],
                "schedule": {
                    "records": [
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
            },
        ]

        blueprint.remove_train(train2)
        assert len(blueprint.entities) == 4
        assert blueprint.to_dict()["blueprint"]["schedules"] == [
            {
                "locomotives": [1],
                "schedule": {
                    "records": [
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
            },
            {
                "locomotives": [3],
                "schedule": {
                    "records": [
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
        test_string = """0eNq1mcty2yAUQH8lw1rJ6AFIeNcuuuquy47HI8vYYSKDB2Gnnoz/vSA/pLRK5nKT7CzMPYAu6ID0QpbtXu6s0o7MXohqjO7I7PcL6dRG120o0/VWkhmxtWrJKSFKr+QfMstO84RI7ZRT8hzRXxwXer9dSusrJNfIVm7q5njfOY/YPLr7npSQnel8sNGhDQ8seJGQo49jhW9lpaxszv/SU/IfPI+GMzi8iIaXcDiNhgs4nMXCywwO59HwiISW0fCIhFbR8IiEimh4REKzNJZeRWQ0i16jVURKs+hFWkXkNButUtOYrXHqIKeYfMSUul62ctGajeqcarrF86Py11tzUHpDZuu67WRCjFW+sfpMSR9yNtV89DquIuZUFr2Qq5hJNazkQNUebnbvMdk/zIR019tDftZP8u5He9SaTDVVwpq6PfvL102FOTS09ev86+77ZFMVWjgCcM8E2jgAep7CJjPnIyZqMpdTkznP0MaDDC5HKw9CL9DOg9CHZd7UdmPun+uNr/uO6z6QmbC3OvgiYz1J79t2qkMMbWHIcDlawxB6ifYwhF6hRQyhC6Bu0o/Og0ndFPh9AGBwBX4fAKHj9wEQeoEWMYRO0SKG0BlWWZwB6ByrLBC9xDoDRK+wzgDRBdYZEDpNoc7IR9AvdAbNsM4ADTfHOgNEL7DOANEp7Kleio9mavKpThlWWaDBcawzQPQS6wwQvcI6A0QXcWfHT047S7HKggyOZVhlgeh53NmRl++cHa/nuW9T5zlWYOVYZoBxUKwcQXSGlSOIPizs2jrVttIe35QMFw8Z4/m488iZnAytLeq9Mwvn7SZdH+PsXk71tMRqHHQfKqzGQXSBtSaEzlOsNUH04Rmwbvdq9fYWhH/W7JjqRY51N2iMBVaeIDrFyhNEZ0ABFV+ZHo41OGiIJdbgIHqFVSiILrAK/Z8+98JrHuVq314+kw0JD9d+B0rFqE4A+mhjV5fPcBOyTMhzrdyiMXrVd+Jc01N3tZULd9yFjhvr611+r/25gJzmYaRTL1OjeXK7c8cAnJ/68TnTPIVwfR72tee+NLynPzfbX4T3nMu6/0XHxX6xra0JnyBHNcS4hpgMpLfa9FXxwKO3QJqOa4jJwGDWSyDPRuXheXotZ9dIxsc1bsW8/zKqnNz6OzV8XE3IQdquv/V+RQsqBGM540WenU5/AR24zCE="""
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

        assert blueprint.find_tile((0, 0))[0] is blueprint.tiles[0]
        assert blueprint.find_tile((10, 10))[0] is blueprint.tiles[1]
        with pytest.raises(IndexError):
            blueprint.find_tile((5, 5))[0].position = (15, 15)

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

        blueprint.rotate(4)

        assert blueprint.entities[0].tile_position == Vector(-1, 0)
        assert blueprint.entities[1].tile_position == Vector(-5, 4)
        assert blueprint.entities[2].tile_position == Vector(-3, 1)
        assert blueprint.entities[2].direction == 4
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
        assert blueprint.entities[2].direction == 8
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
