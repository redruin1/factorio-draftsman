# test_lab.py

from draftsman.entity import Lab, labs
from draftsman.error import InvalidEntityError
from draftsman.warning import DraftsmanWarning

from unittest import TestCase

class LabTesting(TestCase):
    def test_contstructor_init(self):
        lab = Lab()

        with self.assertWarns(DraftsmanWarning):
            Lab(unused_keyword = "whatever")

        with self.assertRaises(InvalidEntityError):
            Lab("this is not a lab")
