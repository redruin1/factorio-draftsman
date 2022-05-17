# spatiallike.py
# -*- encoding: utf-8 -*-

import abc
import six


@six.add_metaclass(abc.ABCMeta)
class SpatialLike(object):
    """
    Abstract class that provides the necessary methods so that an object that
    can be added to a :py:class:`~draftsman.classes.spatialhashmap.SpatialHashMap`.
    """

    @abc.abstractproperty
    def position(self):  # pragma: no coverage
        """
        Position of the object, expressed in local space.
        """
        pass

    @abc.abstractproperty
    def global_position(self):  # pragma: no coverage
        """
        Position of the object, expressed in global space.
        """
        pass

    @abc.abstractproperty
    def collision_box(self):  # pragma: no coverage
        """
        Axis-aligned bounding box of the object where it's position coordinate
        acts as the origin.
        """
        pass

    @abc.abstractproperty
    def collision_mask(self):  # pragma: no coverage
        """
        A set of strings representing the layers that this object collides with.
        """
        pass

    def get_area(self):
        # type: () -> list
        """
        Gets the world-space coordinate AABB of the object. Equivalent to the
        object's ``collision_box`` offset by it's ``position``.

        :returns: The offset collision box, in world-space coordinates.
        """
        return [
            [
                self.collision_box[0][0] + self.global_position["x"],
                self.collision_box[0][1] + self.global_position["y"],
            ],
            [
                self.collision_box[1][0] + self.global_position["x"],
                self.collision_box[1][1] + self.global_position["y"],
            ],
        ]
