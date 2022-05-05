# test_tilelist.py

from __future__ import absolute_import, unicode_literals

from draftsman.classes.blueprint import Blueprint
from draftsman.classes.tile import Tile
from draftsman.error import UnreasonablySizedBlueprintError
from draftsman.warning import OverlappingObjectsWarning

import sys

if sys.version_info >= (3, 3):  # pragma: no coverage
    import unittest
else:  # pragma: no coverage
    import unittest2 as unittest


class TileListTesting(unittest.TestCase):
    def test_constructor(self):
        pass

    def test_insert(self):
        blueprint = Blueprint()

        blueprint.tiles.insert(0, "landfill")
        blueprint.tiles.insert(1, "refined-concrete", position=(1, 1))
        self.assertEqual(blueprint.tiles.data, [blueprint.tiles[0], blueprint.tiles[1]])

        with self.assertWarns(OverlappingObjectsWarning):
            blueprint.tiles.insert(2, "landfill")

        with self.assertRaises(TypeError):
            blueprint.tiles.insert(0, TypeError)

        with self.assertRaises(UnreasonablySizedBlueprintError):
            blueprint.tiles.insert(0, "landfill", position=(-15000, 0))

    def test_getitem(self):
        pass

    def test_setitem(self):
        blueprint = Blueprint()

        blueprint.tiles.insert(0, "landfill")
        blueprint.tiles.insert(1, "refined-concrete", position=(1, 1))

        blueprint.tiles[0] = Tile("refined-concrete")

        self.assertEqual(blueprint.tiles[0].name, "refined-concrete")
        self.assertEqual(blueprint.tiles[1].name, "refined-concrete")

    def test_delitem(self):
        blueprint = Blueprint()

        blueprint.tiles.insert(0, "landfill")
        blueprint.tiles.insert(1, "refined-concrete", position=(1, 1))

        # Int
        del blueprint.tiles[0]

        self.assertEqual(blueprint.tiles[0].name, "refined-concrete")

        # Slice
        del blueprint.tiles[:]

        self.assertEqual(blueprint.tiles.data, [])
