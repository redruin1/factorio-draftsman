# test_heat_pipe.py

from draftsman.entity import HeatPipe, heat_pipes
from draftsman.errors import InvalidEntityID

from unittest import TestCase

class HeatPipeTesting(TestCase):
    def test_default_constructor(self):
        heat_pipe = HeatPipe()
        self.assertEqual(
            heat_pipe.to_dict(),
            {
                "name": "heat-pipe",
                "position": {"x": 0.5, "y": 0.5}
            }
        )

    def test_constructor_init(self):
        heat_pipe = HeatPipe()

        # Warnings
        with self.assertWarns(UserWarning):
            HeatPipe(unused_keyword = "whatever")

        # Errors
        with self.assertRaises(InvalidEntityID):
            HeatPipe("not a heat pipe")