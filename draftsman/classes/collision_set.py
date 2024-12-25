# collision_set.py

from draftsman.classes.vector import Vector

from draftsman.utils import AABB, PrimitiveVector, Shape, extend_aabb

from typing import Union


class CollisionSet:
    """
    An abstraction layer that allows for testing intersections between arbitrary
    types and numbers of shapes. Used primarily for issuing warnings when Entity
    objects are placed such that they overlap each other in ways that would not
    be permitted in game. Almost all entities use a single AABB, but this class
    allows for more handling more complex collisions for rail entities and
    others.
    """

    def __init__(
        self, shapes: list[Shape], position: Union[Vector, PrimitiveVector] = (0, 0)
    ) -> None:
        """
        Create a new collision shape object with the collision shapes ``shapes``.

        :param shapes: A list of :py:class:`Shape` instances, specified in
        relation to the entity's center.
        """
        self.shapes = shapes
        for shape in self.shapes:
            shape.position[0] += position[0]
            shape.position[1] += position[1]

    def get_bounding_box(self) -> AABB:
        """
        Gets the minimum-bounding AABB for this :py:class:`CollisionSet`.

        :returns: An :py:class:`AABB` with the maximal dimensions for this
            ``CollisionSet``, or ``None`` if this ``CollisionSet`` has no shapes.
        """
        if len(self.shapes) == 1:
            return self.shapes[0].get_bounding_box()

        bounding_box = None
        for shape in self.shapes:
            bounding_box = extend_aabb(bounding_box, shape.get_bounding_box())

        return bounding_box

    def overlaps(self, other: "CollisionSet") -> bool:
        """
        Checks to see if any of this :py:class:`CollisionSet` ``shapes``
        intersect any part of ``other``'s ``shapes``.

        :param other: The other :py:class:`CollisionSet` to test against.

        :returns: ``True`` if they overlap, ``False`` if they do not.
        """
        # Simple early-out for most Entities
        if len(self.shapes) == 1 and len(other.shapes) == 1:
            return self.shapes[0].overlaps(other.shapes[0])

        for self_shape in self.shapes:
            for other_shape in other.shapes:
                if self_shape.overlaps(other_shape):
                    return True

        return False

    def rotate(self, amt: int) -> "CollisionSet":
        """
        Rotates all ``shapes`` within this :py:class:`CollisionSet` by ``amt``,
        where ``amt`` is in increments of 45 degrees. Contsructs a new collision
        set with the rotated shapes.

        :param amt: The amount to rotate as multiples of 45 degrees.

        :returns: A new :py:class:`CollisionSet` with the rotated contents.
        """

        # TODO: Update to work with 22.5 degree world.
        rotated_shapes = []

        for shape in self.shapes:
            rotated_shapes.append(shape.rotate(amt))

        return CollisionSet(rotated_shapes)

    def __eq__(self, other: "CollisionSet") -> bool:
        return isinstance(other, CollisionSet) and self.shapes == other.shapes

    def __repr__(self) -> str:  # pragma: no coverage
        return "<CollisionSet>{}".format(self.shapes)  # TODO: better
