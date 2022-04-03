# test_rocket_silo.py
# -*- encoding: utf-8 -*-

from __future__ import unicode_literals

from draftsman.entity import RocketSilo, rocket_silos
from draftsman.error import InvalidEntityError
from draftsman.warning import DraftsmanWarning

import sys

if sys.version_info >= (3, 3):  # pragma: no coverage
    from unittest import TestCase
else:  # pragma: no coverage
    from unittest2 import TestCase


class RocketSiloTesting(TestCase):
    def test_contstructor_init(self):
        silo = RocketSilo(auto_launch=True)
        self.assertEqual(
            silo.to_dict(),
            {
                "name": "rocket-silo",
                "position": {"x": 4.5, "y": 4.5},
                "auto_launch": True,
            },
        )

        with self.assertWarns(DraftsmanWarning):
            RocketSilo(unused_keyword="whatever")

        with self.assertRaises(InvalidEntityError):
            RocketSilo("this is not a rocket silo")
        with self.assertRaises(TypeError):
            RocketSilo(auto_launch="incorrect")
