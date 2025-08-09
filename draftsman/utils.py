# utils.py

"""
Provides a number of common utility functions. These are primarily used
internally by Draftsman, but can be useful outside of that scope and are
provided to the user as-is.
"""

from draftsman.classes.vector import Vector, PrimitiveVector
from draftsman.error import MalformedBlueprintStringError

from abc import ABCMeta, abstractmethod
import base64
import json
import math
from functools import wraps

import attr
from thefuzz import process
from typing import Optional, Union, TYPE_CHECKING
import warnings
import zlib

if TYPE_CHECKING:  # pragma: no coverage
    from draftsman.classes.collection import Collection
    from draftsman.entity import Entity
    from draftsman.tile import Tile
    from draftsman.signatures import StockConnection

# =============================================================================
# Abstract Shape Classes
# =============================================================================


class Shape(metaclass=ABCMeta):
    """
    Abstract Shape class. Must be overwritten with an implementation. Contains a
    single attribute, a PrimitiveVector :py:attr:`position`.
    """

    def __init__(self, position: Vector):
        self.position = Vector.from_other(position)

    @abstractmethod
    def overlaps(self, other: "Shape") -> bool:  # pragma: no coverage
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

    def __init__(
        self,
        x1: float,
        y1: float,
        x2: float,
        y2: float,
        position: Union[Vector, PrimitiveVector] = (0, 0),
    ):
        """
        Axis-Aligned Bounding Box constructor.

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
        self.top_left = Vector(x1, y1)
        # self.top_left = [x1, y1]
        self.bot_right = Vector(x2, y2)
        # self.bot_right = [x2, y2]

        # self.points = [Vector(x1, y1), Vector(x2, y1), Vector(x2, y2), Vector(x1, y2)]
        self.points = [[x1, y1], [x2, y1], [x2, y2], [x1, y2]]
        # self.normals = [Vector(0, -1), Vector(1, 0), Vector(0, 1), Vector(-1, 0)]
        self.normals = [[0, -1], [1, 0], [0, 1], [-1, 0]]

    @staticmethod
    def from_other(aabb: Union[list[float], tuple[float]]) -> "AABB":
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
    def world_top_left(self) -> PrimitiveVector:
        """
        Gets the top left of the :py:class:`.AABB`, as offset by it's ``position``.
        As the attribute suggests, this is typically the top-left of the box in
        world space. Read only.
        """
        return [
            self.top_left[0] + self.position[0],
            self.top_left[1] + self.position[1],
        ]

    @property
    def world_bot_right(self) -> PrimitiveVector:
        """
        Gets the bottom right of the :py:class:`.AABB`, as offset by it's
        ``position``. As the attribute suggests, this is typically the top-left
        of the box in world space. Read only.
        """
        return [
            self.bot_right[0] + self.position[0],
            self.bot_right[1] + self.position[1],
        ]

    def overlaps(self, other: "Shape") -> bool:
        if isinstance(other, AABB):
            return aabb_overlaps_aabb(self, other)
        elif isinstance(other, Rectangle):
            return rect_overlaps_rect(self, other)
        else:
            raise TypeError("Could not resolve '{}' to a Shape".format(other))

    def get_points(self) -> list[PrimitiveVector]:
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

    def get_bounding_box(self) -> "AABB":
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

    def rotate(self, amt: int) -> "AABB":
        """
        Rotates the :py:class:`.AABB` by increments of 90 degrees and returns a
        new transformed instance.

        ``amt`` is expressed in increments of :py:data:`.Direction`, such that
        ``4`` is a rotation of 90 degrees clockwise and ``-4`` is a rotation of
        90 degrees counter-clockwise.

        :raises ValueError: If ``amt`` is not % 4, as AABB's can only be rotated
            by 90 degrees.

        :param amt: The amount to rotate, expressed as an increments of 22.5
            degrees.
        """
        if amt % 4 != 0:
            raise ValueError(
                "Cannot rotate an AABB by anything other than 90 degree increments"
            )

        # TODO: do this routine with a lookup table instead of float math and
        # min/max

        rot_top_left = rotate_point(self.top_left, math.radians(amt * 22.5))
        rot_bot_right = rotate_point(self.bot_right, math.radians(amt * 22.5))

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

    def __eq__(self, other: "AABB") -> bool:
        return (
            isinstance(other, AABB)
            and self.position == other.position
            and self.top_left == other.top_left
            and self.bot_right == other.bot_right
        )

    def __add__(self, other: Union[PrimitiveVector, Vector]) -> "AABB":
        other = Vector.from_other(other)
        return AABB(*self.top_left, *self.bot_right, self.position + other)

    def __repr__(self) -> str:  # pragma: no coverage
        return "AABB({}, {}, {}, {}) at {}".format(
            self.top_left[0],
            self.top_left[1],
            self.bot_right[0],
            self.bot_right[1],
            self.position,
        )


# TODO: move this
PrimitiveAABB = tuple[PrimitiveVector, PrimitiveVector]


class Rectangle(Shape):
    """
    A rotate-able rectangle abstraction class, distinguished from
    :py:class:`.AABB`. Specified as a ``width``, ``height``, an ``angle``, and a
    ``position`` (it's center).
    """

    def __init__(
        self,
        position: Union[Vector, PrimitiveVector],
        width: float,
        height: float,
        angle: float,
    ):
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

    def overlaps(self, other: "Shape") -> bool:
        return rect_overlaps_rect(self, other)

    def get_points(self) -> list[PrimitiveVector]:
        """
        Returns all 4 points associated with the corners of the Rectangle, used
        for determining collision.

        :returns: a ``list`` of 4 :py:class:`.Vector` objects for each of the
            Rectangle's corners.
        """
        rot_points = [
            rotate_point(point, math.radians(self.angle)) for point in self.points
        ]
        return [
            [point[0] + self.position[0], point[1] + self.position[1]]
            for point in rot_points
        ]

    def get_bounding_box(self) -> AABB:
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

    def rotate(self, amt: int) -> "Rectangle":
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
            rotate_point(self.position, math.radians(amt * 22.5)),
            self.width,
            self.height,
            self.angle + amt * 22.5,
        )

    def __eq__(self, other: "Rectangle") -> bool:
        return (
            isinstance(other, Rectangle)
            and self.position == other.position
            and self.width == other.width
            and self.height == other.height
            and self.angle == other.angle
        )

    def __repr__(self) -> str:  # pragma: no coverage
        return "Rectangle({}, {}, {}, {})".format(
            self.position, self.width, self.height, self.angle
        )


# =============================================================================
# Encoding/Decoding Operations
# =============================================================================


def string_to_JSON(string: str) -> dict:
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
    except Exception as e:
        raise MalformedBlueprintStringError(e)


def JSON_to_string(JSON: dict) -> str:
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


def encode_version(major: int, minor: int, patch: int = 0, dev_ver: int = 0) -> int:
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


def decode_version(version_number: int) -> tuple[int, int, int, int]:
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


def version_string_to_tuple(version_string: str) -> tuple[int, int, int, int]:
    """
    Converts a version string to a tuple.

    Used extensively when parsing mod versions when updating the package's data,
    provided to the user for convinience. Splits a string by the dot character
    and converts each component to an ``int``. Pads the string with trailing
    zeros in order to match the 4-component version format Factorio uses.

    For the inverse operation, see :py:func:`version_tuple_to_string`.

    :param version_string: The version string to separate.

    :returns: A 4-length tuple of the format ``(a, b, c, 0)`` from ``"a.b.c"``
    """
    output = [int(elem) for elem in version_string.split(".")]
    return tuple(output + [0] * (4 - len(output)))


def version_tuple_to_string(version_tuple: tuple[int, ...]) -> str:
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


def distance(point1: PrimitiveVector, point2: PrimitiveVector) -> float:
    """
    Gets the Euclidean distance between two points. This is mostly just for
    Python 2 compatability.

    :param point1: The first point to check between.
    :param point2: The first point to check between.

    :returns: The distance between.
    """
    return math.sqrt((point1[0] - point2[0]) ** 2 + (point1[1] - point2[1]) ** 2)


def rotate_point(a: PrimitiveVector, angle: float) -> PrimitiveVector:
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


def dot_product(a: PrimitiveVector, b: PrimitiveVector) -> float:
    """
    Gets the dot product between two 2D vectors.

    :param a: The first vector.
    :parma b: The second vector.

    :returns: The dot product of ``a`` and ``b``.
    """
    return a[0] * b[0] + a[1] * b[1]


def magnitude(a: PrimitiveVector) -> float:
    """
    Gets the magnitude of a point.

    :param a: The input vector to get the magnitude of.

    :returns: The distance from the origin of point ``a``.
    """
    return math.sqrt(dot_product(a, a))


def normalize(a: PrimitiveVector) -> PrimitiveVector:
    """
    Normalizes a vector such that it's magnitude is equal to 1.

    :param a: The input vector to normalize.

    :returns: A new PrimitiveVector equivalent to normalized ``a``.
    """
    mag = float(magnitude(a))
    return [a[0] / mag, a[1] / mag]


def perpendicular(a: PrimitiveVector) -> PrimitiveVector:
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


def point_in_aabb(p: PrimitiveVector, a: AABB) -> bool:
    """
    Checks to see if a PrimitiveVector ``p`` is located inside AABB ``a``.

    :param p: A :py:class:`Vector` with a first and second element.
    :param a: An :py:class:`AABB` with the region to check against.

    :returns: ``True`` if the point is inside the box, ``False`` otherwise.
    """
    return (p[0] >= a.world_top_left[0] and p[0] <= a.world_bot_right[0]) and (
        p[1] >= a.world_top_left[1] and p[1] <= a.world_bot_right[1]
    )


def aabb_overlaps_aabb(a: AABB, b: AABB) -> bool:
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


def point_in_circle(p: PrimitiveVector, r: float, c: PrimitiveVector = (0, 0)) -> bool:
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


def aabb_overlaps_circle(a: AABB, r: float, c: PrimitiveVector) -> bool:
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


def flatten_points_on(
    points: list[PrimitiveVector], axis: PrimitiveVector, result: PrimitiveVector
):
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


def is_separating_axis(
    a_points: list[PrimitiveVector],
    b_points: list[PrimitiveVector],
    axis: PrimitiveVector,
):
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


def rect_overlaps_rect(a: Rectangle, b: Rectangle) -> bool:
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


def extend_aabb(a: Optional[AABB], b: Optional[AABB]) -> Optional[AABB]:
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


def aabb_to_dimensions(aabb: Optional[AABB]) -> tuple[int, int]:
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

    # if not isinstance(aabb, AABB):
    #     aabb = AABB(aabb[0][0], aabb[0][1], aabb[1][0], aabb[1][1])

    x = int(math.ceil(aabb.bot_right[0] - aabb.top_left[0]))
    y = int(math.ceil(aabb.bot_right[1] - aabb.top_left[1]))

    return (x, y)


# =============================================================================
# Miscellaneous
# =============================================================================


def dict_merge(a: dict, b: dict) -> dict:
    """
    Merge two dictionaries together. Modifies ``a`` inplace. If keys exist in
    both dictionaries, keys from ``b`` overwrite keys in ``a``.
    """
    for key in b:
        if key in a:
            if isinstance(a[key], dict) and isinstance(b[key], dict):
                dict_merge(a[key], b[key])
            else:
                a[key] = b[key]
        else:
            a[key] = b[key]
    return a


def get_first(entity_names: list[str]):
    """
    Because python has no convenient `get` equivalent for lists, we use this
    method to return the first element of the list and ``None`` otherwise. Used
    to grab the default entity name if one is not supplied to the constructor
    of an Entity.

    :param entity_names: The list of entities to attempt to get the first entry
        from.

    :returns: ``entity_names[0]``, or ``None`` if no such entry exists.
    """
    try:
        return entity_names[0]
    except IndexError:
        return None


def flatten_entities(collection: "Collection") -> list["Entity"]:
    """
    Iterates over a :py:class:`.Collection` with nested structures and returns a
    1D, "flattened" list of those entities.

    :param collection: The :py:class:`.Collection` instance to grab the entities
        from.

    :returns: A ``list`` containing all the entities in breadth-first sequence.
    """
    out = []

    for entity in collection.entities:
        result = entity.get()
        if isinstance(result, list):
            out.extend(result)
        else:
            out.append(result)
    for group in collection.groups:
        out.extend(flatten_entities(group))

    return out


def flatten_tiles(collection: "Collection") -> list["Tile"]:
    """
    Iterates over a :py:class:`.Collection` with nested structures and returns a
    1D, "flattened" list of those tiles.

    :param collection: The :py:class:`.Collection` instance to grab the tiles
        from.

    :returns: A ``list`` containing all the tiles in breadth-first sequence.
    """

    out = [tile for tile in collection.tiles]

    for group in collection.groups:
        out.extend(flatten_tiles(group))

    return out


def flatten_stock_connections(collection: "Collection") -> list["StockConnection"]:
    """
    Iterates over a :py:class:`.Collection` with nested structures and returns a
    1D, "flattened" list of those stock connections.

    :param collection: The :py:class:`.Collection` instance to grab the entities
        from.

    :returns: A ``list`` containing all the entities in breadth-first sequence.
    """
    out = [connection for connection in collection.stock_connections]

    for group in collection.groups:
        out.extend(flatten_stock_connections(group))

    return out


def parse_energy(energy_string: str) -> int:
    """
    Converts a Factorio energy description string into a integer number of
    Joules or Watts. Valid inputs match the following regex string::

        "[0..9]+[kKMGTPEZY]?[JW]"

    Correctly formatted strings start with a valid integer, followed by an
    optional magnitude character, finished with either "J" for Joules or "W" for
    Watts.

    Behaves identically to ``util.parse_energy`` in Factorio's source; if
    a Watt string is input, it will convert the output result to Joules/tick
    instead of Joules/second (1/60th Watts).

    :param energy_string: The correctly formatted input string to parse.
    :returns: a properly-scaled integer representing the Joule or Watt amount
        input.

    :raises ValueError: If the input string is missing it's Joule/Watt
        identifier, it's magnitude character is not recognized, or if the string
        remainder cannot be parsed to an integer.
    """
    energy_chars = {
        "k": 10**3,
        "K": 10**3,
        "M": 10**6,
        "G": 10**9,
        "T": 10**12,
        "P": 10**15,
        "E": 10**18,
        "Z": 10**21,
        "Y": 10**24,
    }

    ending = energy_string[-1]
    if ending not in {"J", "W"}:
        raise ValueError("'{}' missing Joule or Watts specifier".format(energy_string))

    multiplier = 1 / 60 if ending == "W" else 1
    magnitude = energy_string[-2:-1]
    if magnitude.isalpha():
        if magnitude not in energy_chars:
            raise ValueError("Unrecognized magnitude character '{}'".format(magnitude))
        multiplier = multiplier * energy_chars[magnitude]
        digits_string = energy_string[:-2]
    else:
        digits_string = energy_string[:-1]

    return round(int(digits_string) * multiplier)


def passes_surface_conditions(conditions: list[dict], properties: dict) -> bool:
    """
    Checks to see if a set of surface conditions passes a set of surface
    properties. Used when checking whether an entity or a recipe is valid on a
    particular planet.
    """
    if conditions is None:
        return True

    for condition in conditions:
        property_name = condition["property"]
        # if property_name in properties:
        value = properties[property_name]
        min_val = condition.get("min", -math.inf)
        max_val = condition.get("max", math.inf)
        if not (min_val <= value <= max_val):
            return False

    return True


# def ignore_traceback(func):
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
    """
    Function decorator that catches all warnings issued from a function and
    re-issues them to the calling function.

    :param func: The function who's errors are caught and re-issued.

    :returns: The result of the function.
    """

    @wraps(func)
    def inner(*args, **kwargs):
        with warnings.catch_warnings(record=True) as warning_list:
            result = func(*args, **kwargs)  # === @reissue_warnings === #

        for warning in warning_list:
            warnings.warn(warning.message, warning.category, stacklevel=2)

        return result

    return inner


def get_suggestion(name, choices, n=3, cutoff=60):
    """
    Looks for similarly-named strings from ``choices`` and suggests ``n``
    results, provided they lie above ``cutoff``.

    :param name: The unrecognized name to look for alternatives to.
    :param choices: An iterable containing valid choices to search.
    :param n: The maximum number of suggestions to return, provided there are
        more than ``n`` options.
    :param cutoff: The minimum "similarity score", where suggestions with lower
        scores than this are ignored.

    :returns: A string intended to be appended to an error or warning message,
        containing the suggested alternative(s).
    """
    # if name is None:
    #     return ""
    suggestions = [
        suggestion[0]
        for suggestion in process.extract(name, choices, limit=n)
        if suggestion[1] >= cutoff
    ]
    if len(suggestions) == 0:
        return ""
    elif len(suggestions) == 1:
        return "; did you mean '{}'?".format(suggestions[0])
    else:
        return "; did you mean one of {}?".format(suggestions)  # pragma: no coverage
        # return "; did you mean one of {}?".format(", ".join(["or " + str(item) if i == len(suggestions) - 1 else str(item) for i, item in enumerate(suggestions)]))


def fix_incorrect_pre_init(cls):  # pragma: no coverage
    """
    Attrs erroneously passes default values to `__attrs_pre_init__` even when
    given values during init. We add a sentinel value to the pre-init call so
    that it only runs once when we tell it to (with the actually correct args).
    """
    original_init = cls.__init__

    @reissue_warnings
    @wraps(original_init)
    def new_init(self, *args, **kwargs):
        self.__attrs_pre_init__(*args, first_call=True, **kwargs)
        original_init(self, *args, **kwargs)

    cls.__init__ = new_init

    return cls


def attrs_reuse(attribute: attr.Attribute, **field_kwargs):  # pragma: no coverage
    """
    Takes a frozen attribute and returns a _CountingAttr object for inheritance
    purposes.
    """
    args = {
        "validator": attribute.validator,
        "repr": attribute.repr,
        "cmp": None,
        "hash": attribute.hash,
        "init": attribute.init,
        "converter": attribute.converter,
        "metadata": attribute.metadata,
        "type": attribute.type,
        "kw_only": attribute.kw_only,
        "eq": attribute.eq,
        "order": attribute.order,
        "on_setattr": attribute.on_setattr,
        "alias": attribute.alias,
    }

    # Map the single "validator" object back down to it's aliased pair.
    # Additionally, we help the user out a little bit by automatically
    # overwriting the compliment `default` or `factory` function when
    # overriding; so if a field already has a `default=3`, using
    # `reuse(factory=lambda: 3)` won't complain about having both kinds of
    # defaults defined.
    if "default" not in field_kwargs and "factory" not in field_kwargs:
        if isinstance(attribute.default, attr.Factory):
            field_kwargs["factory"] = attribute.default.factory
        else:
            field_kwargs["default"] = attribute.default

    args.update(field_kwargs)

    # Send through attrib so we reuse the same errors + syntax sugar
    return attr.attrib(**args)


def calculate_occupied_slots(item_requests: list, inventory_id: int) -> int:
    """
    Calculates the number of slots occupied by ``item_requests`` for a
    particular inventory ``inventory_id``.
    """
    return len(
        {
            location.stack
            for item_request in item_requests
            for location in item_request.items.in_inventory
            if location.inventory == inventory_id  # <- Entity specific
        }
    )
