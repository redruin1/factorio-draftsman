# spatial_data_structure.py
# -*- encoding: utf-8 -*-

import abc
import six

from typing import Sequence, TYPE_CHECKING

if TYPE_CHECKING:  # pragma: no coverage
    from draftsman.classes.spatiallike import SpatialLike
    from draftsman.utils import Point, AABB


@six.add_metaclass(abc.ABCMeta)
class SpatialDataStructure(object):
    """
    An abstract class used to implement some kind of spatial querying
    accelleration, such as a spatial hash-map or quadtree.
    """

    @abc.abstractmethod
    def add(self, item, merge=False):  # pragma: no coverage
        # type: (SpatialLike, bool) -> None
        """
        Add a :py:class:`.SpatialLike` instance to the :py:class:`.SpatialHashMap`.

        :param: The object to add.
        """
        pass

    @abc.abstractmethod
    def recursive_add(self, item, merge=False):  # pragma: no coverage
        # type: (SpatialLike, bool) -> None
        """
        Add the leaf-most entities to the hashmap.

        This is used for Groups and other EntityCollections, where you need to
        add the Group's children to the hashmap instead of the Group itself.
        Works with as many nested Groups as desired.

        :param item: The object to add, or its children (if it has any).
        """
        pass

    @abc.abstractmethod
    def remove(self, item):  # pragma: no coverage
        # type: (SpatialLike) -> None
        """
        Remove the ``SpatialLike`` instance from the ``SpatialHashMap``.

        :param item: The object to remove.
        """
        pass

    @abc.abstractmethod
    def recursive_remove(self, item):  # pragma: no coverage
        # type: (SpatialLike) -> None
        """
        Inverse of :py:meth:`recursive_add`.

        :param item: The object to remove, or its children (if it has any).
        """
        pass

    @abc.abstractmethod
    def clear(self):  # pragma: no coverage
        # type: () -> None
        """
        Deletes all entries in the structure.
        """
        pass

    @abc.abstractmethod
    def get_all_entities(self):  # pragma: no coverage
        # type: () -> list[SpatialLike]
        """
        Get all the entities in the hash map. Iterates over every cell and
        returns the contents sequentially. Useful if you want to get all the
        Entities in a Blueprint without including structural ones like Groups.

        :returns: A ``list`` of all entities inside the hash map.
        """
        pass

    @abc.abstractmethod
    def get_in_radius(self, radius, point, limit=None):  # pragma: no coverage
        # type: (float, Sequence[float], int) -> list[SpatialLike]
        """
        Get all the entities whose ``collision_set`` overlaps a circle.

        :param radius: The radius of the circle.
        :param pos: The center of the circle; Can be specified as a sequence or
            as a ``dict`` with ``"x"`` and ``"y"`` keys.
        :param limit: A maximum amount of entities to return.

        :returns: A ``list`` of all entities that intersect the region. Can be
            empty.
        """
        pass

    @abc.abstractmethod
    def get_on_point(self, point, limit=None):  # pragma: no coverage
        # type: (Point, int) -> list[SpatialLike]
        """
        Get all the entities whose ``collision_set`` overlaps a point.

        :param point: The position to examine; Can be specified as a
            PrimitiveVector or Vector.
        :param limit: A maximum amount of entities to return.

        :returns: A ``list`` of all entities that intersect the point. Can be
            empty.
        """
        pass

    @abc.abstractmethod
    def get_in_area(self, area, limit=None):  # pragma: no coverage
        # type: (AABB, int) -> list[SpatialLike]
        """
        Get all the entities whose ``collision_box`` overlaps an area.

        :param area: The area to examine; specified in the format
            ``[[float, float], [float, float]]``.
        :param limit: A maximum amount of entities to return.

        :returns: A ``list`` of all entities that intersect the point. Can be
            empty.
        """
        pass
