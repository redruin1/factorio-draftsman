# test_player_port.py
# -*- encoding: utf-8 -*-

from __future__ import unicode_literals

from draftsman.entity import PlayerPort, player_ports
from draftsman.error import InvalidEntityError
from draftsman.warning import DraftsmanWarning

import sys

if sys.version_info >= (3, 3):  # pragma: no coverage
    import unittest
else:  # pragma: no coverage
    import unittest2 as unittest


class PlayerPortTesting(unittest.TestCase):
    def test_contstructor_init(self):
        turret = PlayerPort()

        with self.assertWarns(DraftsmanWarning):
            PlayerPort(unused_keyword="whatever")

        with self.assertRaises(InvalidEntityError):
            PlayerPort("this is not a player port")

    def test_mergable_with(self):
        port1 = PlayerPort("player-port")
        port2 = PlayerPort("player-port", tags={"some": "stuff"})

        self.assertTrue(port1.mergable_with(port1))

        self.assertTrue(port1.mergable_with(port2))
        self.assertTrue(port2.mergable_with(port1))

        port2.tile_position = (1, 1)
        self.assertFalse(port1.mergable_with(port2))

    def test_merge(self):
        port1 = PlayerPort("player-port")
        port2 = PlayerPort("player-port", tags={"some": "stuff"})

        port1.merge(port2)
        del port2

        self.assertEqual(port1.tags, {"some": "stuff"})
