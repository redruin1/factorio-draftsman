# vector.py

"""
TODO
"""

from pydantic import BaseModel, ConfigDict
from typing import Union, Callable

PrimitiveVector = tuple[Union[int, float], Union[int, float]]
PrimitiveIntVector = tuple[int, int]
PrimitiveFloatVector = tuple[float, float]


class Vector(object):
    """
    A simple 2d vector class, used to aid in developent and user experience.
    """

    def __init__(self, x: Union[float, int], y: Union[float, int]):
        """
        Constructs a new :py:class:`.Vector`.

        :param x: The x value.
        :param y: The y value.
        """
        self._data = [0, 0]
        self.update(x, y)

    @property
    def x(self) -> Union[float, int]:
        """
        The x-coordinate of the point. Returns either a ``float`` or an ``int``,
        depending on the :py:class:`.Vector` queried.

        :getter: Gets the x-coordinate.
        :setter: Sets the x-coordinate.
        :type: Either ``float`` or ``int``.
        """
        return self._data[0]

    @x.setter
    def x(self, value: Union[float, int]):
        self._data[0] = value

    @property
    def y(self) -> Union[float, int]:
        """
        The y-coordinate of the vector. Returns either a ``float`` or an ``int``,
        depending on the :py:class:`.Vector` queried.

        :getter: Gets the y-coordinate.
        :setter: Sets the y-coordinate.
        :type: Either ``float`` or ``int``.
        """
        return self._data[1]

    @y.setter
    def y(self, value: Union[float, int]):
        self._data[1] = value

    # =========================================================================

    @staticmethod
    def from_other(
        other: Union["Vector", PrimitiveVector], type_cast: Callable = float
    ) -> "Vector":
        """
        Converts a PrimitiveVector into a :py:class:`.Vector`. Also handles the
        case where a :py:class:`.Vector` is already passed in, in which case that
        instance is simply returned. Otherwise, a new :py:class:`.Vector` is
        constructed, populated, and returned.

        :param point: The PrimitiveVector
        :param type_cast: The internal type to store data as.

        :returns: A new :py:class:`.Vector` with the same position as ``point``.
        """
        if isinstance(other, Vector):
            return other
        elif isinstance(other, (tuple, list)):
            return Vector(type_cast(other[0]), type_cast(other[1]))
        elif isinstance(other, dict):
            return Vector(type_cast(other["x"]), type_cast(other["y"]))
        else:
            raise TypeError("Could not resolve '{}' to a Vector object".format(other))

    def update(self, x: Union[float, int], y: Union[float, int]) -> None:
        """
        Updates the data of the existing vector in-place. Useful for preserving
        linked vectors.
        """
        self._data[0] = x
        self._data[1] = y

    def update_from_other(
        self, other: Union["Vector", PrimitiveVector], type_cast: Callable = float
    ) -> None:
        """
        Updates the data of the existing vector in-place from a variable input
        format.

        :param other: The object to get the new set of data from
        :param type_cast: The data type to coerce the input variables towards.
        """
        if isinstance(other, Vector):
            self.update(other.x, other.y)
        elif isinstance(other, (tuple, list)):
            self.update(type_cast(other[0]), type_cast(other[1]))
        elif isinstance(other, dict):
            self.update(type_cast(other["x"]), type_cast(other["y"]))
        else:
            raise TypeError("Could not resolve '{}' to a Vector object".format(other))

    def to_dict(self) -> dict:
        """
        Convert this vector to a Factorio-parseable dict with "x" and "y" keys.

        :returns: A dict of the format ``{"x": x, "y": y}``.
        """
        return {"x": self._data[0], "y": self._data[1]}

    # =========================================================================

    def __getitem__(self, index: Union[str, int]) -> Union[float, int]:
        if index == "x":
            return self._data[0]
        elif index == "y":
            return self._data[1]
        else:
            return self._data[index]

    def __setitem__(self, index: Union[str, int], value: Union[float, int]):
        if index == "x":
            self._data[0] = value
        elif index == "y":
            self._data[1] = value
        else:
            self._data[index] = value

    def __add__(self, other: Union["Vector", PrimitiveVector, float, int]) -> "Vector":
        try:
            return Vector(self[0] + other[0], self[1] + other[1])
        except TypeError:
            return Vector(self[0] + other, self[1] + other)

    def __sub__(self, other: Union["Vector", PrimitiveVector, float, int]) -> "Vector":
        try:
            return Vector(self[0] - other[0], self[1] - other[1])
        except TypeError:
            return Vector(self[0] - other, self[1] - other)

    def __mul__(self, other: Union["Vector", PrimitiveVector, float, int]) -> "Vector":
        try:
            return Vector(self[0] * other[0], self[1] * other[1])
        except TypeError:
            return Vector(self[0] * other, self[1] * other)

    def __truediv__(
        self, other: Union["Vector", PrimitiveVector, float, int]
    ) -> "Vector":
        try:
            return Vector(self[0] / other[0], self[1] / other[1])
        except TypeError:
            return Vector(self[0] / other, self[1] / other)

    __div__ = __truediv__

    def __floordiv__(
        self, other: Union["Vector", PrimitiveVector, float, int]
    ) -> "Vector":
        try:
            return Vector(self[0] // other[0], self[1] // other[1])
        except TypeError:
            return Vector(self[0] // other, self[1] // other)

    def __eq__(self, other) -> bool:
        return isinstance(other, Vector) and self.x == other.x and self.y == other.y

    def __abs__(self) -> "Vector":
        return Vector(abs(self[0]), abs(self[1]))

    def __round__(self, precision: int = 0) -> "Vector":
        return Vector(round(self[0], precision), round(self[1], precision))

    def __str__(self) -> str:  # pragma: no coverage
        return "({}, {})".format(self._data[0], self._data[1])

    def __repr__(self) -> str:  # pragma: no coverage
        return "<Vector>({}, {})".format(self._data[0], self._data[1])
