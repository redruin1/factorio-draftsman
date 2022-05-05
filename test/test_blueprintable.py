# test_blueprintable.py
# -*- encoding: utf-8 -*-

from draftsman.blueprintable import *
from draftsman.error import MalformedBlueprintStringError, IncorrectBlueprintTypeError
from draftsman.utils import JSON_to_string

import sys

if sys.version_info >= (3, 3):  # pragma: no coverage
    import unittest
else:  # pragma: no coverage
    import unittest2 as unittest


class BlueprintUtilsTesting(unittest.TestCase):
    def test_get_blueprintable_from_string(self):
        # Valid Format
        blueprintable = get_blueprintable_from_string(
            "0eNqrVkrKKU0tKMrMK1GyqlbKLEnNVbJCEtNRKkstKs7Mz1OyMrIwNDG3NDI3sTQ1MTc1rq0FAHmyE1c="
        )
        self.assertIsInstance(blueprintable, Blueprint)
        # Valid format, but blueprint book string
        blueprintable = get_blueprintable_from_string(
            "0eNqrVkrKKU0tKMrMK4lPys/PVrKqVsosSc1VskJI6IIldJQSk0syy1LjM/NSUiuUrAx0lMpSi4oz8/OUrIwsDE3MLY3MTSxNTcxNjWtrAVWjHQY="
        )
        self.assertIsInstance(blueprintable, BlueprintBook)
        # Invalid format
        with self.assertRaises(MalformedBlueprintStringError):
            get_blueprintable_from_string("0lmaothisiswrong")

        example = JSON_to_string({"incorrect": {}})
        with self.assertRaises(IncorrectBlueprintTypeError):
            get_blueprintable_from_string(example)
