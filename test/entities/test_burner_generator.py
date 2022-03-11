# test_burner_generator.py

from draftsman.entity import BurnerGenerator, burner_generators
from draftsman.error import InvalidEntityError
from draftsman.warning import DraftsmanWarning

from unittest import TestCase

class BurnerGeneratorTesting(TestCase):
    def test_contstructor_init(self):
        generator = BurnerGenerator()

        with self.assertWarns(DraftsmanWarning):
            BurnerGenerator(unused_keyword = "whatever")

        with self.assertRaises(InvalidEntityError):
            BurnerGenerator("this is not a burner generator")