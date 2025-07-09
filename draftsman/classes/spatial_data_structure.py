# spatial_data_structure.py

from draftsman.classes.spatial_like import SpatialLike
from draftsman.classes.vector import PrimitiveVector
from draftsman.utils import AABB

import abc
from typing import Optional


class SpatialDataStructure(metaclass=abc.ABCMeta):
    """
    An abstract class used to implement some kind of spatial querying
    accelleration, such as a spatial hash-map or quadtree.
    """

    @abc.abstractmethod
    def add(
        self, item: SpatialLike, merge: bool = False
    ) -> Optional[SpatialLike]:  # pragma: no coverage
        """
        Add a :py:class:`.SpatialLike` instance to the :py:class:`.SpatialDataStructure`.

        :param item: The object to add.
        :param merge: Whether or not to attempt to merge the added item with any
            existing item, if possible.

        :returns: The input SpatialLike if properly added, or ``None`` if the
            input object was merged.
        """
        pass

    @abc.abstractmethod
    def remove(self, item: SpatialLike) -> None:  # pragma: no coverage
        """
        Remove the ``SpatialLike`` instance from the ``SpatialHashMap``.

        :param item: The object to remove.
        """
        pass

    @abc.abstractmethod
    def clear(self) -> None:  # pragma: no coverage
        """
        Deletes all entries in the structure.
        """
        pass

    @abc.abstractmethod
    def validate_insert(
        self, item: SpatialLike, merge: bool
    ) -> None:  # pragma: no coverage
        """
        Checks to see if the added object overlaps any other objects currently
        contained within the map, and issues errors or warnings correspondingly.
        """
        pass

    @abc.abstractmethod
    def get_all_entities(self) -> list[SpatialLike]:  # pragma: no coverage
        """
        Get all the entities in the hash map. Iterates over every cell and
        returns the contents sequentially. Useful if you want to get all the
        Entities in a Blueprint without including structural ones like Groups.

        :returns: A ``list`` of all entities inside the hash map.
        """
        pass

    @abc.abstractmethod
    def get_in_radius(
        self, radius: float, point: PrimitiveVector, limit: Optional[int] = None
    ) -> list[SpatialLike]:  # pragma: no coverage
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
    def get_on_point(
        self, point: PrimitiveVector, limit: Optional[int] = None
    ) -> list[SpatialLike]:  # pragma: no coverage
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
    def get_in_aabb(
        self, aabb: AABB, limit: Optional[int] = None
    ) -> list[SpatialLike]:  # pragma: no coverage
        """
        Get all the entities whose ``collision_set`` overlaps an AABB.

        :param aabb: The AABB to examine.
        :param limit: A maximum amount of entities to return.

        :returns: A ``list`` of all entities that intersect the area. Can be
            empty.
        """
        pass
