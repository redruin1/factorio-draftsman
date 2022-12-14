# tile.py
# -*- encoding: utf-8 -*-

from draftsman.tile import Tile
from draftsman.error import InvalidTileError

import sys
import pytest

if sys.version_info >= (3, 3):  # pragma: no coverage
    import unittest
else:  # pragma: no coverage
    import unittest2 as unittest


class TileTesting(unittest.TestCase):
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
        with pytest.raises(InvalidTileError):
            tile = Tile("weeeeee")
            issues = tile.inspect()
            for error in issues:
                raise error

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
        with pytest.raises(InvalidTileError):
            tile.name = "weeeeee"
            issues = tile.inspect()
            for error in issues:
                raise error

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

    def test_to_dict(self):
        tile = Tile("landfill", position=(123, 123))
        assert tile.to_dict() == {"name": "landfill", "position": {"x": 123, "y": 123}}

    # def test_repr(self):
    #     tile = Tile("concrete", (0, 0))
    #     self.assertEqual(
    #         repr(tile), "<Tile>{'name': 'concrete', 'position': {'x': 0, 'y': 0}}"
    #     )
