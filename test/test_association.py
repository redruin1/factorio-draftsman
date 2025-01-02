# test_association.py

from draftsman.classes.association import Association
from draftsman.classes.blueprint import Blueprint
from draftsman.entity import Container
from draftsman.error import InvalidAssociationError

import sys
import pytest
import weakref


class TestAssociation:
    def test_constructor(self):
        test = Container("wooden-chest")
        Association(test)  # No fail

        # Damn cyclic imports
        # TODO: return this code

        # class NonEntity(object):
        #     pass

        # with self.assertRaises(TypeError):
        #     Association(NonEntity()) # Fail

    def test_eq(self):
        test = Container("wooden-chest")
        association1 = Association(test)
        association2 = Association(test)

        assert association1 == association2

        test2 = Container("wooden-chest")
        association3 = Association(test2)

        assert test == test2
        assert association1 != association3

        # Also test against unrelated object
        assert association1 != test

    def test_deepcopy(self):
        blueprint = Blueprint()

        blueprint.entities.append("wooden-chest")
        blueprint.entities.append("wooden-chest", tile_position=(1, 0))

        assert (
            weakref.getweakrefcount(blueprint.entities[0]) == 1
        )  # 1 from the association held by position/tile_position
        assert (
            weakref.getweakrefcount(blueprint.entities[1]) == 1
        )  # (which is cursed, but)

        blueprint.add_circuit_connection("red", 0, 1)

        # print(weakref.getweakrefs(blueprint.entities[0]))

        assert weakref.getweakrefcount(blueprint.entities[0]) == 2
        assert weakref.getweakrefcount(blueprint.entities[1]) == 2

        del blueprint.entities[1]

        # print(weakref.getweakrefs(blueprint.entities[0]))
        # print(blueprint.wires)

        assert (
            weakref.getweakrefcount(blueprint.entities[0]) == 2
        )  # Association in the wire doesn't go away

        with pytest.raises(InvalidAssociationError):
            blueprint.to_dict()
