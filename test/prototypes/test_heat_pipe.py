# test_heat_pipe.py

from draftsman.entity import HeatPipe, heat_pipes, Container
from draftsman.error import InvalidEntityError
from draftsman.warning import UnknownEntityWarning, UnknownKeywordWarning

from collections.abc import Hashable
import pytest


@pytest.fixture
def valid_heat_pipe():
    if len(heat_pipes) == 0:
        return None
    return HeatPipe(
        "heat-pipe",
        id="test",
        quality="uncommon",
        tile_position=(1, 1),
        tags={"blah": "blah"},
    )


class TestHeatPipe:
    def test_constructor_init(self):
        heat_pipe = HeatPipe()

        # Warnings
        with pytest.warns(UnknownEntityWarning):
            HeatPipe("not a heat pipe").validate().reissue_all()

    def test_mergable_with(self):
        pipe1 = HeatPipe("heat-pipe")
        pipe2 = HeatPipe("heat-pipe", tags={"some": "stuff"})

        assert pipe1.mergable_with(pipe1)

        assert pipe1.mergable_with(pipe2)
        assert pipe2.mergable_with(pipe1)

        pipe2.tile_position = (1, 1)
        assert not pipe1.mergable_with(pipe2)

    def test_merge(self):
        pipe1 = HeatPipe("heat-pipe")
        pipe2 = HeatPipe("heat-pipe", tags={"some": "stuff"})

        pipe1.merge(pipe2)
        del pipe2

        assert pipe1.tags == {"some": "stuff"}

    def test_eq(self):
        pipe1 = HeatPipe("heat-pipe")
        pipe2 = HeatPipe("heat-pipe")

        assert pipe1 == pipe2

        pipe1.tags = {"some": "stuff"}

        assert pipe1 != pipe2

        container = Container()

        assert pipe1 != container
        assert pipe2 != container

        # hashable
        assert isinstance(pipe1, Hashable)
