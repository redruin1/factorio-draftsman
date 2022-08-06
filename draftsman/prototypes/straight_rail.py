# straight_rail.py
# -*- encoding: utf-8 -*-

from __future__ import unicode_literals

from draftsman.constants import Direction
from draftsman.classes.collisionset import CollisionSet
from draftsman.classes.entity import Entity
from draftsman.classes.mixins import DoubleGridAlignedMixin, EightWayDirectionalMixin
from draftsman.utils import AABB, Rectangle
from draftsman.warning import DraftsmanWarning

from draftsman.data.entities import straight_rails
from draftsman.data import entities

import warnings


class StraightRail(DoubleGridAlignedMixin, EightWayDirectionalMixin, Entity):
    """
    A straight rail entity.
    """

    def __init__(self, name=straight_rails[0], **kwargs):
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
        eps = 0.001
        vertical_collision = CollisionSet([AABB(-0.75, -1.0 + eps, 0.75, 1.0 - eps)])
        horizontal_collision = vertical_collision.rotate(2)
        diagonal_collision = CollisionSet([Rectangle((-0.5, -0.5), 1.25, 1.40, 45)])
        self._collision_set = vertical_collision
        self._collision_set_rotation = {}
        self._collision_set_rotation[Direction.NORTH] = vertical_collision
        self._collision_set_rotation[Direction.NORTHEAST] = diagonal_collision.rotate(2)
        self._collision_set_rotation[Direction.EAST] = horizontal_collision
        self._collision_set_rotation[Direction.SOUTHEAST] = diagonal_collision.rotate(4)
        self._collision_set_rotation[Direction.SOUTH] = vertical_collision
        self._collision_set_rotation[Direction.SOUTHWEST] = diagonal_collision.rotate(
            -2
        )
        self._collision_set_rotation[Direction.WEST] = horizontal_collision
        self._collision_set_rotation[
            Direction.NORTHWEST
        ] = diagonal_collision  # .rotate(4)

        super(StraightRail, self).__init__(name, straight_rails, **kwargs)

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
