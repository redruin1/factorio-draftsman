# # test_straight_rail.py

# from draftsman.blueprintable import Blueprint
# from draftsman.constants import Direction
# from draftsman.entity import StraightRail, straight_rails, Container
# from draftsman.warning import (
#     DraftsmanWarning,
#     GridAlignmentWarning,
#     OverlappingObjectsWarning,
#     UnknownEntityWarning,
# )

# from collections.abc import Hashable
# import pytest


# class TestStraightRail:
#     def test_constructor_init(self):
#         straight_rail = StraightRail(
#             "straight-rail", tile_position=[0, 0], direction=Direction.NORTHWEST
#         )
#         print(straight_rail.static_collision_set)
#         print(straight_rail.tile_width, straight_rail.tile_height)
#         assert straight_rail.to_dict() == {
#             "name": "straight-rail",
#             "position": {"x": 1.0, "y": 1.0},
#             "direction": 7,
#         }

#         straight_rail = StraightRail(
#             "straight-rail", position={"x": 101, "y": 101}, direction=Direction.SOUTH
#         )
#         assert straight_rail.to_dict() == {
#             "name": "straight-rail",
#             "position": {"x": 101.0, "y": 101.0},
#             "direction": 4,
#         }

#         # Warnings:
#         with pytest.warns(DraftsmanWarning):
#             rail = StraightRail("straight-rail", invalid_keyword="whatever")
#             rail.validate().reissue_all()
#         # if entity is not on a grid pos / 2, then warn the user of the incoming
#         # shift
#         with pytest.warns(GridAlignmentWarning):
#             rail = StraightRail("straight-rail", tile_position=[1, 1])
#             rail.validate().reissue_all()

#         # Errors
#         with pytest.warns(UnknownEntityWarning):
#             StraightRail("this is not a straight rail").validate().reissue_all()

#         # Assert validation with no context still works
#         StraightRail.Format.model_validate(straight_rail._root)

#     def test_overlapping(self):
#         blueprint = Blueprint()
#         blueprint.entities.append("straight-rail")
#         # This shouldn't raise a warning
#         blueprint.entities.append("straight-rail", direction=Direction.EAST)

#         # But this should
#         with pytest.warns(OverlappingObjectsWarning):
#             blueprint.entities.append("straight-rail")

#         blueprint = Blueprint()
#         blueprint.entities.append("straight-rail", direction=Direction.NORTH)
#         assert len(blueprint.entities) == 1
#         # This shouldn't raise a warning
#         blueprint.entities.append("gate", direction=Direction.EAST)
#         assert len(blueprint.entities) == 2
#         blueprint.entities.pop()

#         # But this should
#         with pytest.warns(OverlappingObjectsWarning):
#             blueprint.entities.append("gate", direction=Direction.NORTH)

#     def test_power_and_circuit_flags(self):
#         for name in straight_rails:
#             rail = StraightRail(name)
#             assert rail.power_connectable == False
#             assert rail.dual_power_connectable == False
#             assert rail.circuit_connectable == False
#             assert rail.dual_circuit_connectable == False

#     def test_mergable_with(self):
#         rail1 = StraightRail("straight-rail")
#         rail2 = StraightRail("straight-rail", tags={"some": "stuff"})

#         assert rail1.mergable_with(rail1)

#         assert rail1.mergable_with(rail2)
#         assert rail2.mergable_with(rail1)

#         rail2.tile_position = (2, 2)
#         assert not rail1.mergable_with(rail2)

#     def test_merge(self):
#         rail1 = StraightRail("straight-rail")
#         rail2 = StraightRail("straight-rail", tags={"some": "stuff"})

#         rail1.merge(rail2)
#         del rail2

#         assert rail1.tags == {"some": "stuff"}

#     def test_eq(self):
#         rail1 = StraightRail("straight-rail")
#         rail2 = StraightRail("straight-rail")

#         assert rail1 == rail2

#         rail1.tags = {"some": "stuff"}

#         assert rail1 != rail2

#         container = Container()

#         assert rail1 != container
#         assert rail2 != container

#         # hashable
#         assert isinstance(rail1, Hashable)
