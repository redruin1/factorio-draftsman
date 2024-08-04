# test_underground_pipe.py

from draftsman.entity import UndergroundPipe, Container, underground_pipes
from draftsman.error import InvalidEntityError
from draftsman.warning import UnknownEntityWarning, UnknownKeywordWarning

from collections.abc import Hashable
import pytest


class TestUndergroundPipe:
    def test_constructor_init(self):
        # pipe = UndergroundPipe("pipe-to-ground")

        # Warnings
        with pytest.warns(UnknownKeywordWarning):
            pipe = UndergroundPipe("pipe-to-ground", unused_keyword=10)
            pipe.validate().reissue_all()

        # Errors
        with pytest.warns(UnknownEntityWarning):
            pipe = UndergroundPipe("this is not an underground pipe")
            pipe.validate().reissue_all()

    def test_power_and_circuit_flags(self):
        for name in underground_pipes:
            underground_belt = UndergroundPipe(name)
            assert underground_belt.power_connectable == False
            assert underground_belt.dual_power_connectable == False
            assert underground_belt.circuit_connectable == False
            assert underground_belt.dual_circuit_connectable == False

    def test_mergable_with(self):
        pipe1 = UndergroundPipe("pipe-to-ground")
        pipe2 = UndergroundPipe("pipe-to-ground", tags={"some": "stuff"})

        assert pipe1.mergable_with(pipe1)

        assert pipe1.mergable_with(pipe2)
        assert pipe2.mergable_with(pipe1)

        pipe2.tile_position = (1, 1)
        assert not pipe1.mergable_with(pipe2)

    def test_merge(self):
        pipe1 = UndergroundPipe("pipe-to-ground")
        pipe2 = UndergroundPipe("pipe-to-ground", tags={"some": "stuff"})

        pipe1.merge(pipe2)
        del pipe2

        assert pipe1.tags == {"some": "stuff"}

    def test_eq(self):
        pipe1 = UndergroundPipe("pipe-to-ground")
        pipe2 = UndergroundPipe("pipe-to-ground")

        assert pipe1 == pipe2

        pipe1.tags = {"some": "stuff"}

        assert pipe1 != pipe2

        container = Container()

        assert pipe1 != container
        assert pipe2 != container

        # hashable
        assert isinstance(pipe1, Hashable)
