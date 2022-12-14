# test_tilelist.py

from __future__ import absolute_import, unicode_literals

from draftsman.classes.blueprint import Blueprint
from draftsman.classes.tile import Tile
from draftsman.error import UnreasonablySizedBlueprintError
from draftsman.warning import OverlappingObjectsWarning

import sys
import pytest

if sys.version_info >= (3, 3):  # pragma: no coverage
    import unittest
else:  # pragma: no coverage
    import unittest2 as unittest


class TileListTesting(unittest.TestCase):
    def test_constructor(self):
        # test load from blueprint string
        bp_string = "0eNp9j8EOgjAQRP9lzuUAVoH+ivEAuNGNsG1oNRLSf7fFizHGZC67k3m7s6If7+RmlgCzggcrHua4wvNFujHvwuIIBhxogoJ0U558sEJFP/NwQ1RgOdMTpownhcAjvRnOeg5sJVOSW7U7hQWm0GX8ArkuXBPnR0T/j6R722Pmo4fCg2a/Qaqm1HVb1ftDkm5ifAFGbk0H"
        blueprint = Blueprint(bp_string)
        assert blueprint.to_dict()["blueprint"]["tiles"] == [
            {"name": "stone-path", "position": {"x": 293, "y": -41}},
            {"name": "stone-path", "position": {"x": 294, "y": -41}},
        ]

        with pytest.raises(TypeError):
            blueprint.setup(tiles=["not", "a", "tile"])

    def test_insert(self):
        blueprint = Blueprint()

        blueprint.tiles.insert(0, "landfill")
        blueprint.tiles.insert(1, "refined-concrete", position=(1, 1))
        assert blueprint.tiles.data == [blueprint.tiles[0], blueprint.tiles[1]]

        # Test merging
        blueprint.tiles.insert(2, "landfill", merge=True)
        assert blueprint.tiles.data == [blueprint.tiles[0], blueprint.tiles[1]]

        with pytest.warns(OverlappingObjectsWarning):
            blueprint.tiles.insert(2, "landfill")

        with pytest.raises(TypeError):
            blueprint.tiles.insert(0, TypeError)

        with pytest.raises(UnreasonablySizedBlueprintError):
            blueprint.tiles.insert(0, "landfill", position=(-15000, 0))

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

    def test_getitem(self):
        pass

    def test_setitem(self):
        blueprint = Blueprint()

        blueprint.tiles.insert(0, "landfill")
        blueprint.tiles.insert(1, "refined-concrete", position=(1, 1))

        blueprint.tiles[0] = Tile("refined-concrete")

        assert blueprint.tiles[0].name == "refined-concrete"
        assert blueprint.tiles[1].name == "refined-concrete"

    def test_delitem(self):
        blueprint = Blueprint()

        blueprint.tiles.insert(0, "landfill")
        blueprint.tiles.insert(1, "refined-concrete", position=(1, 1))

        # Int
        del blueprint.tiles[0]

        assert blueprint.tiles[0].name == "refined-concrete"

        # Slice
        del blueprint.tiles[:]

        assert blueprint.tiles.data == []
