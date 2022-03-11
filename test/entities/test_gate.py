# test_gate.py

from draftsman.entity import Gate, gates
from draftsman.error import InvalidEntityError
from draftsman.warning import DraftsmanWarning

from unittest import TestCase

class GateTesting(TestCase):
    def test_contstructor_init(self):
        gate = Gate()

        with self.assertWarns(DraftsmanWarning):
            Gate(unused_keyword = "whatever")

        with self.assertRaises(InvalidEntityError):
            Gate("this is not a gate")