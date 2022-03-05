# test_lab.py

from draftsman.entity import Lab, labs
from draftsman.errors import InvalidEntityID

from unittest import TestCase

class LabTesting(TestCase):
    def test_default_constructor(self):
        lab = Lab()
        self.assertEqual(
            lab.to_dict(),
            {
                "name": "lab",
                "position": {"x": 1.5, "y": 1.5}
            }
        )

    def test_contstructor_init(self):
        lab = Lab()

        with self.assertWarns(UserWarning):
            Lab(unused_keyword = "whatever")

        with self.assertRaises(InvalidEntityID):
            Lab("this is not a lab")
