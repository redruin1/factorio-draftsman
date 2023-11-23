# test_pipe.py

from draftsman.entity import Pipe, pipes, Container
from draftsman.warning import UnknownEntityWarning, UnknownKeywordWarning

from collections.abc import Hashable
import pytest


class TestPipe:
    def test_constructor_init(self):
        pipe = Pipe()

        # Warnings
        with pytest.warns(UnknownKeywordWarning):
            Pipe("pipe", unused_keyword=10)
        with pytest.warns(UnknownEntityWarning):
            Pipe("Ceci n'est pas une pipe.")

    def test_mergable_with(self):
        pipe1 = Pipe("pipe")
        pipe2 = Pipe("pipe", tags={"some": "stuff"})

        assert pipe1.mergable_with(pipe1)

        assert pipe1.mergable_with(pipe2)
        assert pipe2.mergable_with(pipe1)

        pipe2.tile_position = (1, 1)
        assert not pipe1.mergable_with(pipe2)

    def test_merge(self):
        pipe1 = Pipe("pipe")
        pipe2 = Pipe("pipe", tags={"some": "stuff"})

        pipe1.merge(pipe2)
        del pipe2

        assert pipe1.tags == {"some": "stuff"}

    def test_eq(self):
        pipe1 = Pipe("pipe")
        pipe2 = Pipe("pipe")

        assert pipe1 == pipe2

        pipe1.tags = {"some": "stuff"}

        assert pipe1 != pipe2

        container = Container()

        assert pipe1 != container
        assert pipe2 != container

        # hashable
        assert isinstance(pipe1, Hashable)
