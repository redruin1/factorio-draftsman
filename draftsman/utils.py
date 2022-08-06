# utils.py
# -*- encoding: utf-8 -*-

"""
Provides a number of common utility functions. These are primarily used 
internally by Draftsman, but can be useful outside of that scope and are 
provided to the user as-is.
"""

from __future__ import unicode_literals, division

from draftsman.classes.vector import Vector, PrimitiveVector
from draftsman.error import MalformedBlueprintStringError

from abc import ABCMeta, abstractmethod
import base64
import json
import math
from functools import wraps
import six
import sys
from typing import Any, Union
import warnings
import zlib

# =============================================================================
# Abstract Shape Classes
# =============================================================================


@six.add_metaclass(ABCMeta)
class Shape:
    """
    Abstract Shape class. Must be overwritten with an implementation. Contains a
    single attribute, a PrimitiveVector :py:attr:`position`.
    """

    def __init__(self, position):
        # type: (Vector) -> None
        self.position = [position[0], position[1]]

    @abstractmethod
    def overlaps(self, other):  # pragma: no coverage
        # type: (Shape) -> bool
        """
        Determines if this :py:class:`.Shape` overlaps with another
        :py:class:`.Shape`.

        :param other: The other :py:class:`.Shape` to check for intersection.

        :returns: ``True`` if the two shapes overlap, ``False`` otherwise.
        """
        pass


class AABB(Shape):
    """
    Axis-Aligned Bounding-Box abstraction class. Contains a :py:attr:`top_left`
    point and a :py:attr:`bot_right` point, as well as an offset position.
    Provides an abstraction for :py:class:`.CollisionSet` and a number of
    convenience functions.
    """

    def __init__(self, x1, y1, x2, y2, position=[0, 0]):
        # type: (float, float, float, float, Vector) -> None
        """
        TODO

        .. NOTE::

            In this case, "local" coordinates are defined around the origin;
            this can be thought of as the AABB's position in relation to the
            center of the entity it's associated with. By contrast, "world"
            coordinates are the positition of the AABB after offsetting by
            :py:attr:`position`

        .. NOTE::

            Performs no-checks to ensure that :py:attr:`top_left` is actually
            less than :py:attr:`top_right`; that is left as the user's
            responsibility.

        :param x1: The x-coordinate of ``top_left``, in local coordinates.
        :param y1: The y-coordinate of ``top_left``, in local coordinates.
        :param x2: The x-coordinate of ``bot_right``, in local coordinates.
        :param y2: The y-coordinate of ``bot_right``, in local coordinates.
        :param position: The offset position of the AABB, used for positioning
            in world space.
        """
        super(AABB, self).__init__(position)
        # self.top_left = Vector(x1, y1)
        self.top_left = [x1, y1]
        # self.bot_right = Vector(x2, y2)
        self.bot_right = [x2, y2]

        # self.points = [Vector(x1, y1), Vector(x2, y1), Vector(x2, y2), Vector(x1, y2)]
        self.points = [[x1, y1], [x2, y1], [x2, y2], [x1, y2]]
        # self.normals = [Vector(0, -1), Vector(1, 0), Vector(0, 1), Vector(-1, 0)]
        self.normals = [[0, -1], [1, 0], [0, 1], [-1, 0]]

    @staticmethod
    def from_other(aabb):
        # type: (Union[list[float], tuple[float]]) -> AABB
        """
        Converts a ``PrimitiveAABB`` to an :py:class:`.AABB`.

        :param aabb: A ``PrimitiveAABB`` to convert from.

        :returns: An :py:class:`AABB` instance.
        """
        if isinstance(aabb, AABB):
            return aabb
        try:
            return AABB(aabb[0], aabb[1], aabb[2], aabb[3])
        except IndexError:
            raise TypeError("Could not resolve '{}' to an AABB".format(aabb))

    @property
    def world_top_left(self):
        # type: () -> PrimitiveVector
        """
        Gets the top left of the :py:class:`.AABB`, as offset by it's ``position``.
        As the attribute suggests, this is typically the top-left of the box in
        world space. Read only.

        :type: PrimitiveVector
        """
        return [
            self.top_left[0] + self.position[0],
            self.top_left[1] + self.position[1],
        ]

    @property
    def world_bot_right(self):
        # type: () -> PrimitiveVector
        """
        Gets the bottom right of the :py:class:`.AABB`, as offset by it's
        ``position``. As the attribute suggests, this is typically the top-left
        of the box in world space. Read only.

        :type: PrimitiveVector
        """
        return [
            self.bot_right[0] + self.position[0],
            self.bot_right[1] + self.position[1],
        ]

    def overlaps(self, other):
        # type: (Shape) -> bool
        if isinstance(other, AABB):
            return aabb_overlaps_aabb(self, other)
        elif isinstance(other, Rectangle):
            return rect_overlaps_rect(self, other)
        else:
            raise TypeError("Could not resolve '{}' to a Shape".format(other))

    def get_points(self):
        # type: () -> list[Vector]
        """
        Returns all 4 points associated with the corners of the AABB, used for
        determining collision.

        :returns: a ``list`` of 4 :py:class:`.Vector` objects for each of the
            AABB corners.
        """
        return [
            [point[0] + self.position[0], point[1] + self.position[1]]
            for point in self.points
        ]

    def get_bounding_box(self):
        # type: () -> AABB
        """
        Returns the minimum-encompassing bounding box around this AABB, which
        happens to be an new AABB offset by this AABB's position. Used for
        broadphase collision-checking in :py:class:`.SpatialDataStructure`.

        :returns: A new :py:class:`.AABB` object with it's top left and bottom
            right offset by this AABB's position, and the new AABB's position at
            ``(0, 0)``.
        """
        bounding_box = AABB(
            self.top_left[0], self.top_left[1], self.bot_right[0], self.bot_right[1]
        )
        bounding_box.top_left[0] += self.position[0]
        bounding_box.top_left[1] += self.position[1]
        bounding_box.bot_right[0] += self.position[0]
        bounding_box.bot_right[1] += self.position[1]
        return bounding_box

    def rotate(self, amt):
        # type: (int) -> AABB
        """
        Rotates the :py:class:`.AABB` by increments of 90 degrees and returns a
        new transformed instance.

        ``amt`` is expressed in increments of :py:data:`.Direction`, such that
        ``2`` is a rotation of 90 degrees clockwise and ``-2`` is a rotation of
        90 degrees counter-clockwise.

        :raises ValueError: If ``amt`` is odd, as AABB's cannot be rotated by
            45 degrees.

        :param amt: The amount to rotate, expressed as an increments of 45
            degrees.
        """
        if amt % 2 != 0:
            raise ValueError("Cannot rotate an AABB by 45 degree increments")

        # TODO: do this routine with a lookup table instead of float math and
        # min/max

        rot_top_left = rotate_vector(self.top_left, math.radians(amt * 45))
        rot_bot_right = rotate_vector(self.bot_right, math.radians(amt * 45))

        # top_left = Vector(
        #     min(rot_top_left.x, rot_bot_right.x), min(rot_top_left.y, rot_bot_right.y)
        # )
        top_left = [
            min(rot_top_left[0], rot_bot_right[0]),
            min(rot_top_left[1], rot_bot_right[1]),
        ]
        # bot_right = Vector(
        #     max(rot_top_left.x, rot_bot_right.x), max(rot_top_left.y, rot_bot_right.y)
        # )
        bot_right = [
            max(rot_top_left[0], rot_bot_right[0]),
            max(rot_top_left[1], rot_bot_right[1]),
        ]

        return AABB(top_left[0], top_left[1], bot_right[0], bot_right[1], self.position)

    def __eq__(self, other):
        # type: (AABB) -> bool
        return (
            isinstance(other, AABB)
            and self.position == other.position
            and self.top_left == other.top_left
            and self.bot_right == other.bot_right
        )

    def __repr__(self):  # pragma: no coverage
        return "<AABB>({}, {}, {}, {}) at {}".format(
            self.top_left[0],
            self.top_left[1],
            self.bot_right[0],
            self.bot_right[1],
            self.position,
        )


PrimitiveAABB = "list[list[float, float], list[float, float]]"


class Rectangle(Shape):
    """
    A rotate-able rectangle abstraction class, distinguished from
    :py:class:`.AABB`. Specified as a ``width``, ``height``, an ``angle``, and a
    ``position`` (it's center).
    """

    def __init__(self, position, width, height, angle):
        # type: (Vector, float, float, float) -> None
        """
        Creates a :py:class:`.Rectangle`. Initializes it's :py:attr:`.points`
        attribute to specify

        :param position: The position of the rectangle's center.
        :param width: The width of the rectangle with it's angle at 0 degrees.
        :param height: The height of the rectangle with it's angle at 0 degrees.
        :param angle: The rectangle's angle of rotation, specified in degrees.
        """
        super(Rectangle, self).__init__(position)
        self.width = width
        self.height = height
        self.angle = angle

        hw = width / 2
        hh = height / 2
        self.points = [[-hw, -hh], [hw, -hh], [hw, hh], [-hw, hh]]

        # Calculate normals
        self.normals = [0] * 4
        rel_points = self.get_points()
        for i in range(len(self.points)):
            p1 = rel_points[i]
            p2 = rel_points[i + 1] if i < len(rel_points) - 1 else rel_points[0]
            edge = [p2[0] - p1[0], p2[1] - p1[1]]
            self.normals[i] = normalize(perpendicular(edge))

    def overlaps(self, other):
        # type: (Shape) -> bool
        return rect_overlaps_rect(self, other)

    def get_points(self):
        # type: () -> list[PrimitiveVector]
        """
        Returns all 4 points associated with the corners of the Rectangle, used
        for determining collision.

        :returns: a ``list`` of 4 :py:class:`.Vector` objects for each of the
            Rectangle's corners.
        """
        rot_points = [
            rotate_vector(point, math.radians(self.angle)) for point in self.points
        ]
        return [
            [point[0] + self.position[0], point[1] + self.position[1]]
            for point in rot_points
        ]

    def get_bounding_box(self):
        # type: () -> AABB
        """
        Returns the minimum-encompassing bounding box around this Rectangle.
        Used for broadphase collision-checking in :py:class:`.SpatialDataStructure`.

        :returns: A new :py:class:`.AABB` object that circumscribes this
            Rectangle, with the returned AABB's position at ``(0, 0)``.
        """
        points = self.get_points()
        x_min = float("inf")
        y_min = float("inf")
        x_max = -float("inf")
        y_max = -float("inf")

        for point in points:
            if point[0] < x_min:
                x_min = point[0]
            elif point[0] > x_max:
                x_max = point[0]
            if point[1] < y_min:
                y_min = point[1]
            elif point[1] > y_max:
                y_max = point[1]

        return AABB(x_min, y_min, x_max, y_max)

    def rotate(self, amt):
        # type: (int) -> Rectangle
        """
        Rotates the :py:class:`.Rectangle` by increments of 45 degrees and
        returns a new transformed instance.

        ``amt`` is expressed in increments of :py:data:`.Direction`, such that
        ``2`` is a rotation of 90 degrees clockwise and ``-2`` is a rotation of
        90 degrees counter-clockwise.

        :param amt: The amount to rotate, expressed as an increments of 45
            degrees.
        """
        return Rectangle(
            rotate_vector(self.position, math.radians(amt * 45)),
            self.width,
            self.height,
            self.angle + amt * 45,
        )

    def __eq__(self, other):
        # type: (Rectangle) -> bool
        return (
            isinstance(other, Rectangle)
            and self.position == other.position
            and self.width == other.width
            and self.height == other.height
            and self.angle == other.angle
        )

    def __repr__(self):  # pragma: no coverage
        return "<Rectangle>({}, {}, {}, {})".format(
            self.position, self.width, self.height, self.angle
        )


# =============================================================================
# Encoding/Decoding Operations
# =============================================================================


def string_to_JSON(string):
    # type: (str) -> dict
    """
    Decodes a Factorio Blueprint string to a readable JSON Dict. Follows the
    data format specification `here <https://wiki.factorio.com/Blueprint_string_format>`_.

    For the inverse operation, see :py:func:`JSON_to_string`.

    :param string: The input Factorio blueprint string.

    :returns: A JSON ``dict`` with the blueprint's components as keys.

    :exception MalformedBlueprintStringError: If the input string is not
        decodable to a JSON object.
    """
    try:
        return json.loads(zlib.decompress(base64.b64decode(string[1:])))
    except Exception:
        raise MalformedBlueprintStringError


def JSON_to_string(JSON):
    # type: (dict) -> str
    """
    Encodes a JSON dict to a Factorio-readable blueprint string.

    Follows the data format specification `here <https://wiki.factorio.com/Blueprint_string_format>`_.

    For the inverse operation, see :py:func:`string_to_JSON`.

    .. NOTE::

        This function does not verify the data before encoding it. Attempting
        to import an incorrectly formatted blueprint ``dict`` will usually
        result with an error in Factorio. If you need format validation,
        consider using :py:class:`.Blueprint` instead.

    :param JSON: The input JSON ``dict`` object.

    :returns: A ``str`` which can be imported into Factorio.
    """
    return "0" + base64.b64encode(
        zlib.compress(json.dumps(JSON, separators=(",", ":")).encode("utf-8"), 9)
    ).decode("utf-8")


def encode_version(major, minor, patch=0, dev_ver=0):
    # type: (int, int, int, int) -> int
    """
    Converts version components to version number.

    Encodes 4 16-bit version numbers into a 64 bit unsigned integer used
    to specify the version of a Factorio Blueprint or Blueprint Book.

    For the inverse operation, see :py:func:`decode_version`.

    :param major:   Major version number.
    :param minor:   Minor version number.
    :param patch:   Patch version number.
    :param dev_ver: Development version number, used internally by Factorio.

    :returns: A 64 bit ``int`` with all components specified.
    """
    return (major << 48) | (minor << 32) | (patch << 16) | (dev_ver)


def decode_version(version_number):
    # type: (int) -> tuple[int, int, int, int]
    """
    Converts version number to version components.
    Decodes a 64 bit unsigned integer into 4 unsigned shorts and returns them
    as a 4-length tuple, which is usually more readable than the combined
    format.

    For the inverse operation, see :py:func:`encode_version`.

    :param version_number: The version number to decode.
    :returns: a 4 length tuple in the format ``(major, minor, patch, dev_ver)``.
    """
    major = int((version_number >> 48) & 0xFFFF)
    minor = int((version_number >> 32) & 0xFFFF)
    patch = int((version_number >> 16) & 0xFFFF)
    dev_ver = int(version_number & 0xFFFF)
    return major, minor, patch, dev_ver


def version_string_to_tuple(version_string):
    # type: (str) -> tuple
    """
    Converts a version string to a tuple.

    Used extensively when parsing mod versions when updating the package's data,
    provided to the user for convinience. Splits a string by the dot character
    and converts each component to an ``int``.

    For the inverse operation, see :py:func:`version_tuple_to_string`.

    :param version_string: The version string to separate.

    :returns: A n-length tuple of the format ``(a, b, c)`` from ``"a.b.c"``
    """
    return tuple([int(elem) for elem in version_string.split(".")])


def version_tuple_to_string(version_tuple):
    # type: (tuple) -> str
    """
    Converts a version tuple to a string.

    Converts each element of the tuple to a string and then joins them with the
    '.' character.

    For the inverse operation, see, :py:func:`version_string_to_tuple`.

    :param version_tuple: The n-length tuple to interpret.

    :returns: A str of the format ``"a.b.c"`` from ``(a, b, c)``
    """
    return ".".join(str(x) for x in version_tuple)


# =============================================================================
# Vector operations
# =============================================================================


def distance(point1, point2):
    # type: (PrimitiveVector, PrimitiveVector) -> float
    """
    Gets the Euclidean distance between two points. This is mostly just for
    Python 2 compatability.

    :param point1: The first point to check between.
    :param point2: The first point to check between.

    :returns: The distance between.
    """
    return math.sqrt((point1[0] - point2[0]) ** 2 + (point1[1] - point2[1]) ** 2)


def rotate_vector(a, angle):  # TODO: change to rotate_point to be consistent
    # type: (PrimitiveVector, float) -> PrimitiveVector
    """
    Rotate a given vector by ``angle`` radians around the origin.

    :param a: The vector to rotate.
    :param angle: The angle to rotate, in radians.

    :returns: A new PrimitiveVector with the resultant rotation.
    """
    return [
        a[0] * math.cos(angle) - a[1] * math.sin(angle),
        a[0] * math.sin(angle) + a[1] * math.cos(angle),
    ]


def dot_product(a, b):
    # type: (PrimitiveVector, PrimitiveVector) -> float
    """
    Gets the dot product between two 2D vectors.

    :param a: The first vector.
    :parma b: The second vector.

    :returns: The dot product of ``a`` and ``b``.
    """
    return a[0] * b[0] + a[1] * b[1]


def magnitude(a):
    # type: (PrimitiveVector) -> float
    """
    Gets the magnitude of a point.

    :param a: The input vector to get the magnitude of.

    :returns: The distance from the origin of point ``a``.
    """
    return math.sqrt(dot_product(a, a))


def normalize(a):
    # type: (PrimitiveVector) -> PrimitiveVector
    """
    Normalizes a vector such that it's magnitude is equal to 1.

    :param a: The input vector to normalize.

    :returns: A new PrimitiveVector equivalent to normalized ``a``.
    """
    mag = float(magnitude(a))
    return [a[0] / mag, a[1] / mag]


def perpendicular(a):
    # type: (PrimitiveVector) -> PrimitiveVector
    """
    Returns a perpendicular 2D vector from another vector. Used to generate
    normal vectors for the Separating Axis Theorem.

    :param a: The original vector to calculate from.

    :returns: A perpendicular vector to ``a``.
    """
    return [a[1], -a[0]]


# =============================================================================
# Collision Functions
# =============================================================================


def point_in_aabb(p, a):
    # type: (PrimitiveVector, AABB) -> bool
    """
    Checks to see if a PrimitiveVector ``p`` is located inside AABB ``a``.

    :param p: A :py:class:`Vector` with a first and second element.
    :param a: An :py:class:`AABB` with the region to check against.

    :returns: ``True`` if the point is inside the box, ``False`` otherwise.
    """
    return (p[0] >= a.world_top_left[0] and p[0] <= a.world_bot_right[0]) and (
        p[1] >= a.world_top_left[1] and p[1] <= a.world_bot_right[1]
    )


def aabb_overlaps_aabb(a, b):
    # type: (AABB, AABB) -> bool
    """
    Checks to see if AABB ``a`` overlaps AABB ``b``.

    :param a: 2-Dimensional list where the first pair is the minimum coordinate
        and the second pair is the maximum coordinate.
    :param b: Another AABB of the same format as ``a``.

    :returns: ``True`` if they overlap, ``False`` otherwise.
    """
    return (
        a.world_top_left[0] < b.world_bot_right[0]
        and a.world_bot_right[0] > b.world_top_left[0]
    ) and (
        a.world_top_left[1] < b.world_bot_right[1]
        and a.world_bot_right[1] > b.world_top_left[1]
    )


def point_in_circle(p, r, c=(0, 0)):
    # type: (PrimitiveVector, float, PrimitiveVector) -> bool
    """
    Checks to see if a point ``p`` lies within radius ``r`` centered around
    point ``c``. If ``c`` is not provided, the origin is assumed.

    :param p: A point sequence with a first and second element.
    :param r: The radius of the circle.
    :param c: A point sequence with a first and second element.

    :returns: ``True`` if the point is within the circle, ``False`` otherwise.
    """
    dx = p[0] - c[0]
    dy = p[1] - c[1]
    return dx * dx + dy * dy <= r * r


def aabb_overlaps_circle(a, r, c):
    # type: (AABB, float, PrimitiveVector) -> bool
    """
    Checks to see if an AABB ``a`` overlaps a circle with radius ``r`` at point
    ``c``. Algorithm pulled from `<https://stackoverflow.com/a/402010/8167625>`_

    :param a: 2-Dimensional list where the first pair is the minimum coordinate
        and the second pair is the maximum coordinate.
    :param r: The radius of the circle.
    :param c: The center of the circle. Defaults to the origin if not specified.

    :returns: ``True`` if the two shapes overlap, ``False`` otherwise.
    """
    aabb_width = a.bot_right[0] - a.top_left[0]
    aabb_height = a.bot_right[1] - a.top_left[1]
    aabb_center = [
        a.top_left[0] + a.position[0] + aabb_width / 2,
        a.top_left[1] + a.position[1] + aabb_height / 2,
    ]
    circle_distance = [abs(c[0] - aabb_center[0]), abs(c[1] - aabb_center[1])]

    if circle_distance[0] > (aabb_width / 2 + r):
        return False
    if circle_distance[1] > (aabb_height / 2 + r):
        return False

    if circle_distance[0] <= (aabb_width / 2):
        return True
    if circle_distance[1] <= (aabb_height / 2):
        return True

    corner_distance_sq = (circle_distance[0] - aabb_width / 2) ** 2 + (
        circle_distance[1] - aabb_height / 2
    ) ** 2

    return corner_distance_sq <= r**2


def flatten_points_on(points, axis, result):
    """
    Maps points along a particular axis, and returns the smallest and largest
    extent along said axis.
    """
    minpoint = float("inf")
    maxpoint = -float("inf")

    for i in range(len(points)):
        dot = dot_product(points[i], axis)
        # dot = points[i].dot(axis)
        if dot < minpoint:
            minpoint = dot
        if dot > maxpoint:
            maxpoint = dot

    result[0] = minpoint
    result[1] = maxpoint


def is_separating_axis(a_points, b_points, axis):
    """
    Checks to see if the points of two quads (when projected onto a face normal)
    have a space in between their encompassed ranges, returning True if there
    is a gap and False if not. Fundamental operatino of the Separating Axis
    Theorem.
    """
    range_a = [0, 0]
    range_b = [0, 0]

    flatten_points_on(a_points, axis, range_a)
    flatten_points_on(b_points, axis, range_b)

    # We use greater or equal than to allow separating lines on edges
    if range_a[0] >= range_b[1] or range_b[0] >= range_a[1]:
        return True

    return False


def rect_overlaps_rect(a, b):
    # type: (Rectangle, Rectangle) -> bool
    """
    Checks to see whether or not two (rotatable) :py:class:`.Rectangles`
    intersect with each other. Sourced from:
    `<https://github.com/qwertyquerty/collision/blob/master/collision/util.py>`_


    :param a: The first :py:class:`.Recangle` to check.
    :param b: The second :py:class:`.Recangle` to check.

    :returns: ``True`` if the two shapes overlap, ``False`` otherwise.
    """

    a_points = a.get_points()
    b_points = b.get_points()

    for n in a.normals:
        if is_separating_axis(a_points, b_points, n):
            return False

    for n in b.normals:
        if is_separating_axis(a_points, b_points, n):
            return False

    return True


def extend_aabb(a, b):
    # type: (Union[AABB, None], Union[AABB, None]) -> Union[AABB, None]
    """
    Gets the minimum AABB that encompasses two other bounding boxes. Used to
    'grow' the size of a bounding box to encompass both inputs.
    If one of the inputs is ``None``, then the opposite is returned; if both are
    ``None``, then ``None`` is returned.

    :param a: The first :py:class:`.AABB` to extend.
    :param b: The second :py:class:`.AABB` to extend.

    :returns: The minumum bounding :py:class:`.AABB` between the two inputs.
    """
    if a is None:
        return b
    elif b is None:
        return a
    else:
        return AABB(
            min(a.world_top_left[0], b.world_top_left[0]),
            min(a.world_top_left[1], b.world_top_left[1]),
            max(a.world_bot_right[0], b.world_bot_right[0]),
            max(a.world_bot_right[1], b.world_bot_right[1]),
        )


def aabb_to_dimensions(aabb):
    # type: (AABB) -> tuple[int, int]
    """
    Gets the tile-dimensions of an AABB, or the minimum number of tiles across
    each axis that the box would have to take up. If the input `aabb` is None,
    the function returns (0, 0).

    :param aabb: 2-Dimensional list where the first pair is the minimum coordinate
        and the second pair is the maximum coordinate.

    :returns: a ``tuple`` of the form ``(tile_width, tile_height)``
    """
    if aabb is None:
        return (0, 0)

    x = int(math.ceil(aabb.bot_right[0] - aabb.top_left[0]))
    y = int(math.ceil(aabb.bot_right[1] - aabb.top_left[1]))

    return (x, y)


def flatten_entities(entities):
    """
    Iterates over a list of entities with nested structures and returns a 1D,
    "flattened" list of those entities.

    :param entities: The list of entities to flatten.

    :returns: A ``list`` containing all the entities in depth-first sequence.
    """
    out = []
    for entity in entities:
        result = entity.get()
        if isinstance(result, list):
            out.extend(flatten_entities(result))
        else:
            out.append(result)
    return out


# =============================================================================
# Miscellaneous
# =============================================================================

# def ignore_traceback(func):
#     # type: (Any) -> Any
#     """
#     Decorator that removes other decorators from traceback.
#     Pulled from https://stackoverflow.com/questions/22825165/can-decorators-be-removed-from-python-exception-tracebacks
#     """
#     @wraps(func)
#     def wrapper_ignore_exctb(*args, **kwargs):
#         try:
#             return func(*args, **kwargs)
#         except Exception:
#             # Code to remove this decorator from traceback
#             exc_type, exc_value, exc_traceback = sys.exc_info()
#             try:
#                 exc_traceback = exc_traceback.tb_next
#                 exc_traceback = exc_traceback.tb_next
#             except Exception:  # pragma: no coverage
#                 pass
#             ex = exc_type(exc_value)
#             ex.__traceback__ = exc_traceback
#             raise ex
#     return wrapper_ignore_exctb


def reissue_warnings(func):
    # type: (Any) -> Any
    """
    Function decorator that catches all warnings issued from a function and
    re-issues them to the calling function.

    :param func: The function who's errors are caught and re-issued.

    :returns: The result of the function.
    """
    # @ignore_traceback
    @wraps(func)
    def inner(*args, **kwargs):
        with warnings.catch_warnings(record=True) as warning_list:
            result = func(*args, **kwargs)

        for warning in warning_list:
            warnings.warn(warning.message, warning.category, stacklevel=2)

        return result

    return inner
