# test_burner_generator.py

from draftsman.entity import BurnerGenerator, burner_generators
from draftsman.errors import InvalidEntityID

from unittest import TestCase

class BurnerGeneratorTesting(TestCase):
    def test_default_constructor(self):
        generator = BurnerGenerator()
        self.assertEqual(
            generator.to_dict(),
            {
                "name": "burner-generator",
                "position": {"x": 1.5, "y": 2.5}
            }
        )

    def test_contstructor_init(self):
        generator = BurnerGenerator()

        with self.assertWarns(UserWarning):
            BurnerGenerator(unused_keyword = "whatever")

        with self.assertRaises(InvalidEntityID):
            BurnerGenerator("this is not a burner generator")