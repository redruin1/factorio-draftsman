# test_vector.py
# -*- encoding: utf-8 -*-

from draftsman.classes.vector import Vector

import sys

if sys.version_info >= (3, 3):  # pragma: no coverage
    import unittest
else:  # pragma: no coverage
    import unittest2 as unittest


class VectorTesting(unittest.TestCase):
    def test_constructor(self):
        point = Vector(10, 2.3)
        assert point.x == 10
        assert point.y == 2.3

    def test_setters(self):
        point = Vector(1, 2)
        point.x = 100
        assert point._data[0] == 100
        assert point.x == 100
        assert point[0] == 100
        assert point["x"] == 100

        point[0] = 200
        assert point._data[0] == 200
        assert point.x == 200
        assert point[0] == 200
        assert point["x"] == 200

        point["x"] = 300
        assert point._data[0] == 300
        assert point.x == 300
        assert point[0] == 300
        assert point["x"] == 300

        point.y = 100
        assert point._data[1] == 100
        assert point.y == 100
        assert point[1] == 100
        assert point["y"] == 100

        point[1] = 200
        assert point._data[1] == 200
        assert point.y == 200
        assert point[1] == 200
        assert point["y"] == 200

        point["y"] = 300
        assert point._data[1] == 300
        assert point.y == 300
        assert point[1] == 300
        assert point["y"] == 300

    def test_from_other(self):
        tuple_point = Vector.from_other((1, 2))
        assert tuple_point == Vector(1.0, 2.0)
        list_point = Vector.from_other([1.2, 2.3], int)
        assert list_point == Vector(1, 2)
        dict_point = Vector.from_other({"x": 1.3, "y": 3.4}, float)
        assert dict_point == Vector(1.3, 3.4)
        original_point = Vector(1, 2)
        point = Vector.from_other(original_point)
        assert point is original_point

    def test_to_dict(self):
        point = Vector(10, 20)
        assert point.to_dict() == {"x": 10, "y": 20}

    def test_add(self):
        # Constant (float)
        point = Vector(1, 1) + 1.0
        assert point == Vector(2.0, 2.0)
        # Constant (int)
        point = Vector(1, 1) + 1
        assert point == Vector(2, 2)
        # Vector
        point = Vector(-1, 0) + Vector(3.5, 2.9)
        assert point == Vector(2.5, 2.9)

    def test_sub(self):
        # Constant (float)
        point = Vector(1, 1) - 1.0
        assert point == Vector(0.0, 0.0)
        # Constant (int)
        point = Vector(1, 1) - 1
        assert point == Vector(0, 0)
        # Vector
        point = Vector(-1, 0) - Vector(3.5, 2.9)
        assert point == Vector(-4.5, -2.9)

    def test_mul(self):
        # Constant (float)
        point = Vector(1, 1) * 1.0
        assert point == Vector(1.0, 1.0)
        # Constant (int)
        point = Vector(1, 1) * 1
        assert point == Vector(1, 1)
        # Vector
        point = Vector(-1, 0) * Vector(3.0, 2.0)
        assert point == Vector(-3.0, 0.0)

    def test_truediv(self):
        # Constant (float)
        point = Vector(1, 1) / 1.0
        assert point == Vector(1.0, 1.0)
        # Constant (int)
        point = Vector(1, 1) / 1
        assert point == Vector(1, 1)
        # Vector
        point = Vector(-1, 0) / Vector(3.0, 2.0)
        assert point == Vector(-1.0 / 3.0, 0.0)

    def test_floordiv(self):
        # Constant (float)
        point = Vector(1, 1) // 1.0
        assert point == Vector(1.0, 1.0)
        # Constant (int)
        point = Vector(1, 1) // 1
        assert point == Vector(1, 1)
        # Vector
        point = Vector(-1, 0) // Vector(3.0, 2.0)
        assert point == Vector(-1.0, 0.0)
