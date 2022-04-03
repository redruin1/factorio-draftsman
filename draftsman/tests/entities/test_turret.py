# test_turret.py
# -*- encoding: utf-8 -*-

from __future__ import unicode_literals

from draftsman.entity import Turret, turrets
from draftsman.error import InvalidEntityError
from draftsman.warning import DraftsmanWarning

import sys

if sys.version_info >= (3, 3):  # pragma: no coverage
    from unittest import TestCase
else:  # pragma: no coverage
    from unittest2 import TestCase


class TurretTesting(TestCase):
    def test_contstructor_init(self):
        turret = Turret()

        with self.assertWarns(DraftsmanWarning):
            Turret(unused_keyword="whatever")

        with self.assertRaises(InvalidEntityError):
            Turret("this is not a turret")
