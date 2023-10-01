# test_player_port.py

from __future__ import unicode_literals

from draftsman.entity import PlayerPort, player_ports
from draftsman.error import InvalidEntityError
from draftsman.warning import DraftsmanWarning

import sys
import pytest

if sys.version_info >= (3, 3):  # pragma: no coverage
    import unittest
else:  # pragma: no coverage
    import unittest2 as unittest


class PlayerPortTesting(unittest.TestCase):
    def test_contstructor_init(self):
        turret = PlayerPort()

        with pytest.warns(DraftsmanWarning):
            PlayerPort(unused_keyword="whatever")

        with pytest.raises(InvalidEntityError):
            PlayerPort("this is not a player port")

    def test_mergable_with(self):
        port1 = PlayerPort("player-port")
        port2 = PlayerPort("player-port", tags={"some": "stuff"})

        assert port1.mergable_with(port2)

        assert port1.mergable_with(port2)
        assert port2.mergable_with(port1)

        port2.tile_position = (1, 1)
        assert not port1.mergable_with(port2)

    def test_merge(self):
        port1 = PlayerPort("player-port")
        port2 = PlayerPort("player-port", tags={"some": "stuff"})

        port1.merge(port2)
        del port2

        assert port1.tags == {"some": "stuff"}
