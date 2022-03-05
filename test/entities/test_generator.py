# test_generator.py

from draftsman.entity import Generator, generators
from draftsman.errors import InvalidEntityID

from unittest import TestCase

class GeneratorTesting(TestCase):
    def test_default_constructor(self):
        generator = Generator()
        self.assertEqual(
            generator.to_dict(),
            {
                "name": "steam-engine",
                "position": {"x": 1.5, "y": 2.5}
            }
        )

    def test_constructor_init(self):
        generator = Generator()

        # Warnings
        with self.assertWarns(UserWarning):
            Generator(unused_keyword = "whatever")

        # Errors
        with self.assertRaises(InvalidEntityID):
            Generator("not a boiler")