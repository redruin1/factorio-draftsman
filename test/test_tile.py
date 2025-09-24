# tile.py

from draftsman.classes.group import Group
from draftsman.classes.vector import Vector
from draftsman.constants import ValidationMode
from draftsman.tile import Tile, new_tile
from draftsman.error import DataFormatError
import draftsman.validators
from draftsman.warning import UnknownTileWarning

import pytest


class TestTile:
    def test_constructor(self):
        # Specific position
        tile = Tile("hazard-concrete-right", (100, -100))
        assert tile.name == "hazard-concrete-right"
        assert tile.position.x == 100
        assert tile.position.y == -100
        # Default position
        tile = Tile("hazard-concrete-right")
        assert tile.name == "hazard-concrete-right"
        assert tile.position.x == 0
        assert tile.position.y == 0

        # Invalid name
        with pytest.warns(UnknownTileWarning, match="Unknown tile 'weeeeee'"):
            tile = Tile("weeeeee")

        # Invalid name with suggestion
        with pytest.warns(
            UnknownTileWarning,
            match="Unknown tile 'stonepath'; did you mean 'stone-path'?",
        ):
            tile = Tile("stonepath")

        # TODO: test closure
        # with self.assertRaises(InvalidTileError):
        #     tile = Tile("incorrect")
        #     with tile.validate() as issues:
        #         for error in issues:
        #             raise error

        # Invalid name with suggestion
        with pytest.warns(
            UnknownTileWarning,
            match="Unknown tile 'stonepath'; did you mean 'stone-path'?",
        ):
            tile = Tile("stonepath")

        # Incorrect type
        with pytest.raises(DataFormatError):
            tile = Tile(name=100)

        # Incorrect type with validation off
        with draftsman.validators.set_mode(ValidationMode.DISABLED):
            tile = Tile(name=100)
        assert tile.name == 100
        with pytest.raises(DataFormatError):
            tile.validate().reissue_all()

    def test_set_name(self):
        tile = Tile("hazard-concrete-left")
        assert tile.name == "hazard-concrete-left"
        assert tile.position.x == 0
        assert tile.position.y == 0
        tile.name = "refined-hazard-concrete-left"
        assert tile.name == "refined-hazard-concrete-left"
        assert tile.position.x == 0
        assert tile.position.y == 0

        # Invalid name
        with pytest.warns(UnknownTileWarning):
            tile.name = "weeeeee"

    def test_set_position(self):
        tile = Tile("landfill", (0, 0))
        tile.position = (-123, 123)
        assert tile.position.x == -123
        assert tile.position.y == 123

        with pytest.raises(DataFormatError):
            tile.position = "incorrect"

    def test_global_position(self):
        tile = Tile("landfill")
        group = Group(position=(100, 100))
        group.tiles.append(tile, copy=False)
        assert tile.position.x == 0
        assert tile.position.y == 0
        assert tile.global_position.x == 100
        assert tile.global_position.y == 100

    def test_to_dict(self):
        tile = Tile("landfill", position=(123, 123))
        assert tile.to_dict() == {"name": "landfill", "position": {"x": 123, "y": 123}}

    # def test_repr(self):
    #     tile = Tile("concrete", (0, 0))
    #     self.assertEqual(
    #         repr(tile), "<Tile>{'name': 'concrete', 'position': {'x': 0, 'y': 0}}"
    #     )


class TestTileFactory:
    def test_new_tile(self):
        # Normal
        tile = new_tile("landfill")
        assert isinstance(tile, Tile)
        assert tile.name == "landfill"

        # Unknown tiles are accepted, but warned
        with pytest.warns(UnknownTileWarning):
            tile = new_tile("unknown")
        assert isinstance(tile, Tile)

        # Draftsman will only complain if you ask it to
        with pytest.warns(UnknownTileWarning):
            tile.validate().reissue_all()

        # Generic entities should be able to handle attribute access and serialization
        assert tile.name == "unknown"
        assert tile.position == Vector(0, 0)
        assert tile.to_dict() == {"name": "unknown", "position": {"x": 0, "y": 0}}

        # You should also be able to set new attributes to them without Draftsman
        # complaining
        with draftsman.validators.set_mode(ValidationMode.MINIMUM):
            tile = Tile.from_dict(
                {
                    "name": "unknown",
                    "position": {"x": 1, "y": 1},
                    "unknown_attribute": "value",
                }
            )
        assert tile.to_dict() == {
            "name": "unknown",
            "position": {"x": 1, "y": 1},
            "unknown_attribute": "value",
        }

        # After construction, as well
        tile.extra_keys["new_thing"] = "extra!"
        assert tile.to_dict() == {
            "name": "unknown",
            "position": {"x": 1, "y": 1},
            "unknown_attribute": "value",
            "new_thing": "extra!",
        }

        # Don't complain if minimum
        tile.validate(mode="minimum").reissue_all()

        # However, setting known attributes incorrectly should still create
        # issues
        tile.validate_assignment = ValidationMode.STRICT
        assert tile.validate_assignment is ValidationMode.STRICT
        with pytest.raises(DataFormatError):
            tile.name = 100
