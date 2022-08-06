# curved_rail.py
# -*- encoding: utf-8 -*-

from __future__ import unicode_literals

from draftsman.classes.collisionset import CollisionSet
from draftsman.classes.entity import Entity
from draftsman.classes.mixins import DoubleGridAlignedMixin, EightWayDirectionalMixin
from draftsman.constants import Direction
from draftsman.utils import AABB, Rectangle
from draftsman.warning import DraftsmanWarning

from draftsman.data.entities import curved_rails
from draftsman.data import entities

import warnings


class CurvedRail(DoubleGridAlignedMixin, EightWayDirectionalMixin, Entity):
    """
    A curved rail entity.
    """

    def __init__(self, name=curved_rails[0], **kwargs):
        # type: (str, **dict) -> None
        """
        TODO
        """

        # This is kinda hacky, but necessary due to Factorio issuing dummy
        # values for collision boxes. We have to do this before initialization
        # of the rest of the class because certain things like tile position are
        # dependent on this information and can be set during initialization
        # (if we pass in arguments in **kwargs).

        # We set a (private) flag to ignore the dummy collision box that
        # Factorio provides
        self._overwritten_collision_set = True
        # We then provide a list of all the custom rotations
        left_turn = CollisionSet(
            [AABB(0.25, 1.8, 1.75, 3.9), Rectangle((-0.375, -0.7175), 1.4, 5.45, -35)]
        )
        right_turn = CollisionSet(
            [AABB(-1.75, 1.8, -0.25, 3.9), Rectangle((0.375, -0.7175), 1.4, 5.45, 35)]
        )
        self._collision_set = left_turn
        self._collision_set_rotation = {}
        self._collision_set_rotation[Direction.NORTH] = left_turn
        self._collision_set_rotation[Direction.NORTHEAST] = right_turn
        self._collision_set_rotation[Direction.EAST] = left_turn.rotate(2)
        self._collision_set_rotation[Direction.SOUTHEAST] = right_turn.rotate(2)
        self._collision_set_rotation[Direction.SOUTH] = left_turn.rotate(4)
        self._collision_set_rotation[Direction.SOUTHWEST] = right_turn.rotate(4)
        self._collision_set_rotation[Direction.WEST] = left_turn.rotate(6)
        self._collision_set_rotation[Direction.NORTHWEST] = right_turn.rotate(6)

        super(CurvedRail, self).__init__(name, curved_rails, **kwargs)

        if "collision_mask" in entities.raw[self.name]:  # pragma: no coverage
            self._collision_mask = set(entities.raw[self.name]["collision_mask"])
        else:  # pragma: no coverage
            self._collision_mask = {
                "item-layer",
                "object-layer",
                "rail-layer",
                "floor-layer",
                "water-tile",
            }

        for unused_arg in self.unused_args:
            warnings.warn(
                "{} has no attribute '{}'".format(type(self), unused_arg),
                DraftsmanWarning,
                stacklevel=2,
            )
