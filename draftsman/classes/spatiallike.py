# spatiallike.py

import abc
import six


@six.add_metaclass(abc.ABCMeta)
class SpatialLike(object):
    """
    Abstract class that provides a template for creating an object that can be
    added to a `SpatialHashMap`.
    """

    @abc.abstractproperty
    def position(self):  # pragma: no coverage
        """
        Position of the object.
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
        Set of strings representing the layers that this object collides with.
        Objects will only collide with one another if their `get_area()`s
        overlap and their `collision_mask`s have at least one similar entry.
        """
        pass

    def get_area(self):
        # type: () -> list
        """
        Gets the world-space coordinate AABB of the object. Equivalent to the sum of the
        object's `position` and it's `collision_box`.
        """
        return [
            [
                self.collision_box[0][0] + self.position["x"],
                self.collision_box[0][1] + self.position["y"],
            ],
            [
                self.collision_box[1][0] + self.position["x"],
                self.collision_box[1][1] + self.position["y"],
            ],
        ]
