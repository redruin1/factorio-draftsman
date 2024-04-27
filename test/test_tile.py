# tile.py

from draftsman.classes.vector import Vector
from draftsman.constants import ValidationMode
from draftsman.tile import Tile, new_tile
from draftsman.error import DataFormatError, InvalidTileError
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

        with pytest.raises(DataFormatError):
            tile = Tile(name=100)

        # validation off
        tile = Tile(name=100, validate="none")
        assert tile.name == 100

        # TODO: test closure
        # with self.assertRaises(InvalidTileError):
        #     tile = Tile("incorrect")
        #     with tile.validate() as issues:
        #         for error in issues:
        #             raise error

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

        # TODO: test closure
        # with self.assertRaises(InvalidTileError):
        #     tile.name = "incorrect"
        #     with tile.validate() as issues:
        #         for error in issues:
        #             raise error

        # TODO: test closure
        # with self.assertRaises(InvalidTileError):
        #     tile.name = "incorrect"
        #     with tile.validate() as issues:
        #         for error in issues:
        #             raise error

    def test_set_position(self):
        tile = Tile("landfill", (0, 0))
        tile.position = (-123, 123)
        assert tile.position.x == -123
        assert tile.position.y == 123

        with pytest.raises(DataFormatError):
            tile._root.position = "incorrect"
            tile.validate().reissue_all()

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

        # Invalid mode
        with pytest.raises(ValueError):
            tile = new_tile("unknown", if_unknown="wrong")

        # Unknown error (default)
        with pytest.raises(InvalidTileError):
            tile = new_tile("unknown", if_unknown="error")

        # Unknown ignore
        tile = new_tile("unknown", if_unknown="ignore")
        assert tile is None

        # Unknown accept
        tile = new_tile("unknown", validate="minimum", if_unknown="accept")
        assert isinstance(tile, Tile)

        # Generic entities should be able to handle attribute access and serialization
        assert tile.name == "unknown"
        assert tile.position == Vector(0, 0)
        assert tile.to_dict() == {"name": "unknown", "position": {"x": 0, "y": 0}}

        # You should also be able to set new attributes to them without Draftsman
        # complaining
        tile = new_tile(
            "unknown",
            position=(1, 1),
            unknown_attribute="value",
            validate="minimum",
            if_unknown="accept",
        )
        assert tile.to_dict() == {
            "name": "unknown",
            "position": {"x": 1, "y": 1},
            "unknown_attribute": "value",
        }

        # After construction, as well
        tile["new_thing"] = "extra!"
        assert tile.to_dict() == {
            "name": "unknown",
            "position": {"x": 1, "y": 1},
            "unknown_attribute": "value",
            "new_thing": "extra!",
        }

        # Draftsman will still complain about the unknown entity, but it doesn't
        # panic unless you want it to
        with pytest.warns(UnknownTileWarning):
            tile.validate(mode=ValidationMode.PEDANTIC).reissue_all()

        # However, setting known attributes incorrectly should still create
        # issues
        with pytest.raises(DataFormatError):
            tile.name = 100
