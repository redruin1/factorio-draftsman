# test_vector.py

from draftsman.classes.vector import Vector

import sys

if sys.version_info >= (3, 3):  # pragma: no coverage
    import unittest
else:  # pragma: no coverage
    import unittest2 as unittest


class VectorTesting(unittest.TestCase):
    def test_constructor(self):
        point = Vector(10, 2.3)
        self.assertEqual(point.x, 10)
        self.assertEqual(point.y, 2.3)

    def test_setters(self):
        point = Vector(1, 2)
        point.x = 100
        self.assertEqual(point.data[0], 100)
        self.assertEqual(point.x, 100)
        self.assertEqual(point[0], 100)
        self.assertEqual(point["x"], 100)

        point[0] = 200
        self.assertEqual(point.data[0], 200)
        self.assertEqual(point.x, 200)
        self.assertEqual(point[0], 200)
        self.assertEqual(point["x"], 200)

        point["x"] = 300
        self.assertEqual(point.data[0], 300)
        self.assertEqual(point.x, 300)
        self.assertEqual(point[0], 300)
        self.assertEqual(point["x"], 300)

        point.y = 100
        self.assertEqual(point.data[1], 100)
        self.assertEqual(point.y, 100)
        self.assertEqual(point[1], 100)
        self.assertEqual(point["y"], 100)

        point[1] = 200
        self.assertEqual(point.data[1], 200)
        self.assertEqual(point.y, 200)
        self.assertEqual(point[1], 200)
        self.assertEqual(point["y"], 200)

        point["y"] = 300
        self.assertEqual(point.data[1], 300)
        self.assertEqual(point.y, 300)
        self.assertEqual(point[1], 300)
        self.assertEqual(point["y"], 300)

    def test_from_other(self):
        tuple_point = Vector.from_other((1, 2))
        self.assertEqual(tuple_point, Vector(1.0, 2.0))
        list_point = Vector.from_other([1.2, 2.3], int)
        self.assertEqual(list_point, Vector(1, 2))
        dict_point = Vector.from_other({"x": 1.3, "y": 3.4}, float)
        self.assertEqual(dict_point, Vector(1.3, 3.4))
        original_point = Vector(1, 2)
        point = Vector.from_other(original_point)
        self.assertIs(point, original_point)

    def test_to_dict(self):
        point = Vector(10, 20)
        self.assertEqual(point.to_dict(), {"x": 10, "y": 20})

    def test_add(self):
        # Constant (float)
        point = Vector(1, 1) + 1.0
        self.assertEqual(point, Vector(2.0, 2.0))
        # Constant (int)
        point = Vector(1, 1) + 1
        self.assertEqual(point, Vector(2, 2))
        # Vector
        point = Vector(-1, 0) + Vector(3.5, 2.9)
        self.assertEqual(point, Vector(2.5, 2.9))

    def test_sub(self):
        # Constant (float)
        point = Vector(1, 1) - 1.0
        self.assertEqual(point, Vector(0.0, 0.0))
        # Constant (int)
        point = Vector(1, 1) - 1
        self.assertEqual(point, Vector(0, 0))
        # Vector
        point = Vector(-1, 0) - Vector(3.5, 2.9)
        self.assertEqual(point, Vector(-4.5, -2.9))

    def test_mul(self):
        # Constant (float)
        point = Vector(1, 1) * 1.0
        self.assertEqual(point, Vector(1.0, 1.0))
        # Constant (int)
        point = Vector(1, 1) * 1
        self.assertEqual(point, Vector(1, 1))
        # Vector
        point = Vector(-1, 0) * Vector(3.0, 2.0)
        self.assertEqual(point, Vector(-3.0, 0.0))

    def test_truediv(self):
        # Constant (float)
        point = Vector(1, 1) / 1.0
        self.assertEqual(point, Vector(1.0, 1.0))
        # Constant (int)
        point = Vector(1, 1) / 1
        self.assertEqual(point, Vector(1, 1))
        # Vector
        point = Vector(-1, 0) / Vector(3.0, 2.0)
        self.assertEqual(point, Vector(-1.0 / 3.0, 0.0))

    def test_floordiv(self):
        # Constant (float)
        point = Vector(1, 1) // 1.0
        self.assertEqual(point, Vector(1.0, 1.0))
        # Constant (int)
        point = Vector(1, 1) // 1
        self.assertEqual(point, Vector(1, 1))
        # Vector
        point = Vector(-1, 0) // Vector(3.0, 2.0)
        self.assertEqual(point, Vector(-1.0, 0.0))
