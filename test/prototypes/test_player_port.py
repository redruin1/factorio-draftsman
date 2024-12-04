# test_player_port.py

from draftsman.entity import PlayerPort, player_ports, Container
from draftsman.warning import UnknownEntityWarning, UnknownKeywordWarning

from typing import Hashable
import pytest

# For compatibility with versions of Factorio post 2.0
if len(player_ports) == 0:
    pytest.skip("No player ports to test", allow_module_level=True)

class TestPlayerPort:
    def test_contstructor_init(self):
        port = PlayerPort()

        with pytest.warns(UnknownKeywordWarning):
            PlayerPort(unused_keyword="whatever").validate().reissue_all()

        with pytest.warns(UnknownEntityWarning):
            PlayerPort("this is not a player port").validate().reissue_all()

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

    def test_eq(self):
        pipe1 = PlayerPort("player-port")
        pipe2 = PlayerPort("player-port")

        assert pipe1 == pipe2

        pipe1.tags = {"some": "stuff"}

        assert pipe1 != pipe2

        container = Container()

        assert pipe1 != container
        assert pipe2 != container

        # hashable
        assert isinstance(pipe1, Hashable)
