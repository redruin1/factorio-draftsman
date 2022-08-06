# vector.py
# -*- encoding: utf-8 -*-

"""
TODO
"""

from __future__ import unicode_literals, division

from typing import Union, Callable

PrimitiveVector = "Sequence[float, float]"


class Vector(object):
    """
    A simple 2d vector class, used to aid in developent and user experience.
    """

    def __init__(self, x, y):
        """
        Constructs a new :py:class:`.Vector`.

        :param x: The x value.
        :param y: The y value.
        """
        self.data = [x, y]

    @property
    def x(self):
        # type: () -> Union[float, int]
        """
        The x-coordinate of the point. Returns either a ``float`` or an ``int``,
        depending on the :py:class:`.Vector` queried.

        :getter: Gets the x-coordinate.
        :setter: Sets the x-coordinate.
        :type: Either ``float`` or ``int``.
        """
        return self.data[0]

    @x.setter
    def x(self, value):
        # type: (Union[float, int]) -> None
        self.data[0] = value

    @property
    def y(self):
        # type: () -> float
        """
        The y-coordinate of the vector. Returns either a ``float`` or an ``int``,
        depending on the :py:class:`.Vector` queried.

        :getter: Gets the y-coordinate.
        :setter: Sets the y-coordinate.
        :type: Either ``float`` or ``int``.
        """
        return self.data[1]

    @y.setter
    def y(self, value):
        # type: (Union[float, int]) -> None
        self.data[1] = value

    # =========================================================================

    @staticmethod
    def from_other(vector, type_cast=float):
        # type: (Union[Vector, PrimitiveVector], Callable) -> Vector
        """
        Converts a PrimitiveVector into a :py:class:`.Vector`. Also handles the
        case where a :py:class:`.Vector` is already passed in, in which case that
        instance is simply returned. Otherwise, a new :py:class:`.Vector` is
        constructed, populated, and returned.

        :param point: The PrimitiveVector
        :param type_cast: The internal type to store data as.

        :returns: A new :py:class:`.Vector` with the same position as ``point``.
        """
        if isinstance(vector, Vector):
            return vector
        elif isinstance(vector, (tuple, list)):
            return Vector(type_cast(vector[0]), type_cast(vector[1]))
        elif isinstance(vector, dict):
            return Vector(type_cast(vector["x"]), type_cast(vector["y"]))
        else:
            raise TypeError("Could not resolve '{}' to a Vector object".format(vector))

    def to_dict(self):
        # type: () -> dict
        """
        Convert this vector to a Factorio-parseable dict with "x" and "y" keys.

        :returns: A dict of the format ``{"x": x, "y": y}``.
        """
        return {"x": self.data[0], "y": self.data[1]}

    # =========================================================================

    def __getitem__(self, index):
        # type: (int) -> Union[float, int]
        if index == "x":
            return self.data[0]
        elif index == "y":
            return self.data[1]
        else:
            return self.data[index]

    def __setitem__(self, index, value):
        # type: (int, Union[float, int]) -> None
        if index == "x":
            self.data[0] = value
        elif index == "y":
            self.data[1] = value
        else:
            self.data[index] = value

    def __add__(self, other):
        # type: (Union[Vector, PrimitiveVector, float, int]) -> Vector
        try:
            return Vector(self[0] + other[0], self[1] + other[1])
        except TypeError:
            return Vector(self[0] + other, self[1] + other)

    def __sub__(self, other):
        # type: (Union[Vector, PrimitiveVector, float, int]) -> Vector
        try:
            return Vector(self[0] - other[0], self[1] - other[1])
        except TypeError:
            return Vector(self[0] - other, self[1] - other)

    def __mul__(self, other):
        # type: (Union[Vector, PrimitiveVector, float, int]) -> Vector
        try:
            return Vector(self[0] * other[0], self[1] * other[1])
        except TypeError:
            return Vector(self[0] * other, self[1] * other)

    def __truediv__(self, other):
        # type: (Union[Vector, float, int]) -> Vector
        try:
            return Vector(self[0] / other[0], self[1] / other[1])
        except TypeError:
            return Vector(self[0] / other, self[1] / other)

    __div__ = __truediv__

    def __floordiv__(self, other):
        # type: (Union[Vector, float, int]) -> Vector
        try:
            return Vector(self[0] // other[0], self[1] // other[1])
        except TypeError:
            return Vector(self[0] // other, self[1] // other)

    def __eq__(self, other):
        # type: (Vector) -> bool
        return isinstance(other, Vector) and self.x == other.x and self.y == other.y

    def __str__(self):  # pragma: no coverage
        # type: () -> str
        return "({}, {})".format(self.data[0], self.data[1])

    def __repr__(self):  # pragma: no coverage
        # type: () -> str
        return "<Vector>({}, {})".format(self.data[0], self.data[1])
