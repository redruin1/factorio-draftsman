# spatiallike.py
# -*- encoding: utf-8 -*-

from draftsman.classes.collision_set import CollisionSet
from draftsman.classes.vector import Vector
from draftsman.utils import AABB

import abc
import copy
import six


@six.add_metaclass(abc.ABCMeta)
class SpatialLike:
    """
    Abstract class that provides the necessary methods so that an object that
    can be added to a :py:class:`~draftsman.classes.spatialhashmap.SpatialHashMap`.
    """

    @abc.abstractproperty
    def position(self) -> Vector:  # pragma: no coverage
        """
        Position of the object, expressed in local space. Local space can be
        either global space (if the EntityLike exists in a Blueprint at a root
        level) or local to it's parent Group.
        """
        pass

    @abc.abstractproperty
    def global_position(self) -> Vector:  # pragma: no coverage
        """
        Position of the object, expressed in global space (world space).
        """
        pass

    @abc.abstractproperty
    def collision_set(self) -> CollisionSet:  # pragma: no coverage
        """
        Set of :py:class:`.CollisionShape` where the Entity's position acts as
        their origin.
        """
        pass

    @abc.abstractproperty
    def collision_mask(self) -> set[str]:  # pragma: no coverage
        """
        A set of strings representing the collision layers that this object
        collides with.
        """
        pass

    def get_world_bounding_box(self) -> AABB:
        """
        Gets the world-space coordinates AABB that completely encompasses the
        ``collision_set`` of this SpatialLike. Behaves similarly to the old
        function `get_area()`, except now it correctly handles non-AABB
        collision shapes.
        """
        # Get the (local) Axis-aligned bounding box
        bounding_box = self.collision_set.get_bounding_box()

        # Offset the bounding box by the global position of the SpatialLike to
        # get the world-space box
        if bounding_box is not None:
            bounding_box.top_left[0] += self.global_position.x
            bounding_box.top_left[1] += self.global_position.y
            bounding_box.bot_right[0] += self.global_position.x
            bounding_box.bot_right[1] += self.global_position.y

        return bounding_box

    def get_world_collision_set(self) -> CollisionSet:
        """
        Get's the world-space coordinate CollisionSet of the object, or the
        collection of all shapes that this EntityLike interacts with.

        :returns: A new :py:class:`.CollisionSet` with it's content's copied.
        """
        # TODO: check if there's a way to not have to copy this
        return CollisionSet(
            copy.deepcopy(self.collision_set.shapes), self.global_position._data
        )
