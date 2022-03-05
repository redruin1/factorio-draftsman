# test_wall.py

from draftsman.entity import Wall, walls
from draftsman.errors import InvalidEntityID, InvalidSignalID

from schema import SchemaError

from unittest import TestCase

class WallTesting(TestCase):
    def test_default_constructor(self):
        wall = Wall()
        self.assertEqual(
            wall.to_dict(),
            {
                "name": "stone-wall",
                "position": {"x": 0.5, "y": 0.5}
            }
        )

    def test_contstructor_init(self):
        wall = Wall()

        with self.assertWarns(UserWarning):
            Wall(unused_keyword = "whatever")

        with self.assertRaises(InvalidEntityID):
            Wall("this is not a wall")

    def test_set_enable_disable(self):
        wall = Wall()
        wall.set_enable_disable(True)
        self.assertEqual(
            wall.control_behavior,
            {
                "circuit_open_gate": True
            }
        )
        wall.set_enable_disable(None)
        self.assertEqual(wall.control_behavior, {})
        with self.assertRaises(SchemaError):
            wall.set_enable_disable("incorrect")

    def test_set_read_gate(self):
        wall = Wall()
        wall.set_read_gate(True)
        self.assertEqual(
            wall.control_behavior,
            {
                "circuit_read_sensor": True
            }
        )
        wall.set_read_gate(None)
        self.assertEqual(wall.control_behavior, {})
        with self.assertRaises(SchemaError):
            wall.set_read_gate("incorrect")

    def test_set_output_signal(self):
        wall = Wall()
        wall.set_output_signal("signal-A")
        self.assertEqual(
            wall.control_behavior,
            {
                "output_signal": {
                    "name": "signal-A",
                    "type": "virtual"
                }
            }
        )
        wall.set_output_signal(None)
        self.assertEqual(wall.control_behavior, {})
        with self.assertRaises(InvalidSignalID):
            wall.set_output_signal("incorrect")