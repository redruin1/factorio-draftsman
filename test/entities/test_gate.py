# test_gate.py

from draftsman.entity import Gate, gates
from draftsman.errors import InvalidEntityID

from unittest import TestCase

class GateTesting(TestCase):
    def test_default_constructor(self):
        gate = Gate()
        self.assertEqual(
            gate.to_dict(),
            {
                "name": "gate",
                "position": {"x": 0.5, "y": 0.5}
            }
        )

    def test_contstructor_init(self):
        gate = Gate()

        with self.assertWarns(UserWarning):
            Gate(unused_keyword = "whatever")

        with self.assertRaises(InvalidEntityID):
            Gate("this is not a gate")