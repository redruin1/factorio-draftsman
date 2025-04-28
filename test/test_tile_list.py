# test_tilelist.py

from draftsman.classes.blueprint import Blueprint
from draftsman.classes.exportable import ValidationResult
from draftsman.classes.tile import Tile
from draftsman.classes.tile_list import TileList
from draftsman.constants import ValidationMode
from draftsman.error import DataFormatError, UnreasonablySizedBlueprintError
from draftsman.warning import OverlappingObjectsWarning

import pytest


class TestTileList:
    def test_constructor(self):
        # test load from blueprint string
        bp_string = "0eNp9j8EOgjAQRP9lzuUAVoH+ivEAuNGNsG1oNRLSf7fFizHGZC67k3m7s6If7+RmlgCzggcrHua4wvNFujHvwuIIBhxogoJ0U558sEJFP/NwQ1RgOdMTpownhcAjvRnOeg5sJVOSW7U7hQWm0GX8ArkuXBPnR0T/j6R722Pmo4fCg2a/Qaqm1HVb1ftDkm5ifAFGbk0H"
        blueprint = Blueprint.from_string(bp_string)
        assert blueprint.to_dict()["blueprint"]["tiles"] == [
            {"name": "stone-path", "position": {"x": 293, "y": -41}},
            {"name": "stone-path", "position": {"x": 294, "y": -41}},
        ]

        with pytest.raises(DataFormatError):
            blueprint.tiles = ["not", "a", "tile"]

    def test_insert(self):
        blueprint = Blueprint()

        blueprint.tiles.insert(0, "landfill")
        blueprint.tiles.insert(1, "refined-concrete", position=(1, 1))
        assert blueprint.tiles._root == [blueprint.tiles[0], blueprint.tiles[1]]

        # Test merging
        blueprint.tiles.insert(2, "landfill", merge=True)
        assert blueprint.tiles._root == [blueprint.tiles[0], blueprint.tiles[1]]

        with pytest.warns(OverlappingObjectsWarning):
            blueprint.tiles.insert(2, "landfill")

        with pytest.raises(TypeError):
            blueprint.tiles.insert(0, TypeError)

        # Test no copy
        blueprint = Blueprint()
        local_tile = Tile("landfill", position=[1, 1])
        blueprint.tiles.append(local_tile, copy=False)
        local_tile.name = "concrete"
        assert local_tile is blueprint.tiles[0]
        assert blueprint.tiles[0].to_dict() == {
            "name": "concrete",
            "position": {"x": 1, "y": 1},
        }

    def test_union(self):
        blueprint1 = Blueprint()
        blueprint1.tiles.append("landfill")

        blueprint2 = Blueprint()
        blueprint2.tiles.append("landfill")
        blueprint2.tiles.append("concrete", position=(1, 0))

        union = Blueprint()
        union.tiles = blueprint1.tiles | blueprint2.tiles

        assert isinstance(union.tiles, TileList)
        assert union.tiles._parent is union
        assert len(union.tiles) == 2
        assert union.tiles._root == [
            Tile("landfill"),
            Tile("concrete", position=(1, 0)),
        ]
        assert union.tiles[0].parent is union
        assert union.tiles[1].parent is union

    def test_intersection(self):
        blueprint1 = Blueprint()
        blueprint1.tiles.append("landfill")

        blueprint2 = Blueprint()
        blueprint2.tiles.append("landfill")
        blueprint2.tiles.append("concrete", position=(1, 0))

        intersection = Blueprint()
        intersection.tiles = blueprint1.tiles & blueprint2.tiles

        assert isinstance(intersection.tiles, TileList)
        assert intersection.tiles._parent is intersection
        assert len(intersection.tiles) == 1
        assert intersection.tiles._root == [
            Tile("landfill"),
        ]
        assert intersection.tiles[0].parent is intersection

        # Intersection with no commonalities
        blueprint3 = Blueprint()
        blueprint3.tiles.append("concrete", position=(1, 1))

        intersection.tiles = blueprint1.tiles & blueprint3.tiles
        assert len(intersection.tiles) == 0

    def test_difference(self):
        blueprint1 = Blueprint()
        blueprint1.tiles.append("landfill")

        blueprint2 = Blueprint()
        blueprint2.tiles.append("landfill")
        blueprint2.tiles.append("concrete", position=(1, 0))

        difference = Blueprint()
        difference.tiles = blueprint2.tiles - blueprint1.tiles

        assert isinstance(difference.tiles, TileList)
        assert difference.tiles._parent is difference
        assert len(difference.tiles) == 1
        assert difference.tiles._root == [Tile("concrete", position=(1, 0))]
        assert difference.tiles[0].parent is difference

    def test_getitem(self):
        pass

    def test_setitem(self):
        blueprint = Blueprint()

        blueprint.tiles.insert(0, "landfill")
        blueprint.tiles.insert(1, "refined-concrete", position=(1, 1))

        blueprint.tiles[0] = Tile("refined-concrete")

        assert blueprint.tiles[0].name == "refined-concrete"
        assert blueprint.tiles[1].name == "refined-concrete"

        # No overlapping warning
        blueprint.tiles.validate_assignment = "none"
        assert blueprint.tiles.validate_assignment == ValidationMode.NONE
        blueprint.tiles[0] = Tile("refined-concrete", position=(1, 1))

        # Incorrect type
        with pytest.raises(TypeError):
            blueprint.tiles[0] = "incorrect"

    def test_delitem(self):
        blueprint = Blueprint()

        blueprint.tiles.insert(0, "landfill")
        blueprint.tiles.insert(1, "refined-concrete", position=(1, 1))

        # Int
        del blueprint.tiles[0]

        assert blueprint.tiles[0].name == "refined-concrete"

        # Slice
        del blueprint.tiles[:]

        assert blueprint.tiles._root == []

    def test_equals(self):
        blueprint = Blueprint()

        # Different types
        assert blueprint.tiles != TypeError

        # Different lengths
        other_blueprint = Blueprint()
        other_blueprint.tiles.append("landfill")
        assert blueprint.tiles != other_blueprint.tiles

        # Different components
        blueprint.tiles.append("concrete")
        assert blueprint.tiles != other_blueprint.tiles

        # True equality
        blueprint.tiles[0] = Tile("landfill")
        assert blueprint.tiles == other_blueprint.tiles

    def test_validate(self):
        blueprint = Blueprint()

        # No validation case
        assert blueprint.tiles.validate(mode="none") == ValidationResult([], [])

        # TODO: reimplement
        # blueprint.tiles.validate_assignment = "none"
        # blueprint.tiles[0] = "incorrect"

        # with pytest.raises(DataFormatError):
        #     blueprint.tiles.validate().reissue_all()
