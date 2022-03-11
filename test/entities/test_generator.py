# test_generator.py

from draftsman.entity import Generator, generators
from draftsman.error import InvalidEntityError
from draftsman.warning import DraftsmanWarning

from unittest import TestCase

class GeneratorTesting(TestCase):
    def test_constructor_init(self):
        generator = Generator()

        # Warnings
        with self.assertWarns(DraftsmanWarning):
            Generator(unused_keyword = "whatever")

        # Errors
        with self.assertRaises(InvalidEntityError):
            Generator("not a boiler")