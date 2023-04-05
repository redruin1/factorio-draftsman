# test_association.py
# -*- encoding: utf-8 -*-

from draftsman.classes.association import Association
from draftsman.classes.blueprint import Blueprint
from draftsman.entity import Container
from draftsman.error import InvalidAssociationError

import sys
import pytest
import weakref

if sys.version_info >= (3, 3):  # pragma: no coverage
    import unittest
else:  # pragma: no coverage
    import unittest2 as unittest


class AssociationTesting(unittest.TestCase):
    def test_constructor(self):
        test = Container("wooden-chest")
        Association(test) # No fail

        # Damn cyclic imports
        # TODO: return this code

        # class NonEntity(object):
        #     pass

        # with self.assertRaises(TypeError):
        #     Association(NonEntity()) # Fail

    def test_deepcopy(self):
        blueprint = Blueprint()

        blueprint.entities.append("wooden-chest")
        blueprint.entities.append("wooden-chest", tile_position=(1, 0))
        blueprint.add_circuit_connection("red", 0, 1)

        assert weakref.getweakrefcount(blueprint.entities[0]) == 2
        assert weakref.getweakrefcount(blueprint.entities[1]) == 2

        del blueprint.entities[1]

        assert weakref.getweakrefcount(blueprint.entities[0]) == 1

        with pytest.raises(InvalidAssociationError):
            blueprint.to_dict()
