# test_splitter.py

from draftsman.constants import Direction
from draftsman.entity import Splitter, splitters, Container
from draftsman.error import DataFormatError, InvalidItemError
from draftsman.warning import (
    UnknownEntityWarning,
    UnknownKeywordWarning,
    UnknownItemWarning,
)

from collections.abc import Hashable
import pytest


class TestSplitter:
    def test_constructor_init(self):
        # Valid
        splitter = Splitter(
            "splitter",
            direction=Direction.EAST,
            tile_position=[1, 1],
            input_priority="left",
            output_priority="right",
            filter="small-lamp",
        )
        assert splitter.to_dict() == {
            "name": "splitter",
            "position": {"x": 1.5, "y": 2.0},
            "direction": 2,
            "input_priority": "left",
            "output_priority": "right",
            "filter": "small-lamp",
        }

        # Warnings
        with pytest.warns(UnknownKeywordWarning):
            Splitter(position=[0, 0], direction=Direction.WEST, invalid_keyword=5).validate().reissue_all()

        with pytest.warns(UnknownEntityWarning):
            Splitter("this is not a splitter").validate().reissue_all()

        # TODO
        # with pytest.raises(UnknownItemWarning):
        #     Splitter("splitter", filter="wrong")

        # Errors
        # Raises errors when any of the associated data is incorrect
        with pytest.raises(TypeError):
            Splitter("splitter", id=25).validate().reissue_all()

        with pytest.raises(TypeError):
            Splitter("splitter", position=TypeError).validate().reissue_all()

        with pytest.raises(DataFormatError):
            Splitter("splitter", direction="incorrect").validate().reissue_all()

        with pytest.raises(DataFormatError):
            Splitter("splitter", input_priority=TypeError).validate().reissue_all()

        with pytest.raises(DataFormatError):
            Splitter("splitter", input_priority="wrong").validate().reissue_all()

        with pytest.raises(DataFormatError):
            Splitter("splitter", output_priority=TypeError).validate().reissue_all()

        with pytest.raises(DataFormatError):
            Splitter("splitter", output_priority="wrong").validate().reissue_all()

        with pytest.raises(DataFormatError):
            Splitter("splitter", filter=TypeError).validate().reissue_all()

    def test_power_and_circuit_flags(self):
        for name in splitters:
            splitter = Splitter(name)
            assert splitter.power_connectable == False
            assert splitter.dual_power_connectable == False
            assert splitter.circuit_connectable == False
            assert splitter.dual_circuit_connectable == False

    def test_mergable_with(self):
        splitter1 = Splitter("splitter")
        splitter2 = Splitter(
            "splitter",
            input_priority="left",
            output_priority="right",
            filter="small-lamp",
            tags={"some": "stuff"},
        )

        assert splitter1.mergable_with(splitter1)

        assert splitter1.mergable_with(splitter2)
        assert splitter2.mergable_with(splitter1)

        splitter2.tile_position = (1, 1)
        assert not splitter1.mergable_with(splitter2)

    def test_merge(self):
        splitter1 = Splitter("splitter")
        splitter2 = Splitter(
            "splitter",
            input_priority="left",
            output_priority="right",
            filter="small-lamp",
            tags={"some": "stuff"},
        )

        splitter1.merge(splitter2)
        del splitter2

        assert splitter1.input_priority == "left"
        assert splitter1.output_priority == "right"
        assert splitter1.filter == "small-lamp"
        assert splitter1.tags == {"some": "stuff"}

    def test_eq(self):
        splitter1 = Splitter("splitter")
        splitter2 = Splitter("splitter")

        assert splitter1 == splitter2

        splitter1.tags = {"some": "stuff"}

        assert splitter1 != splitter2

        container = Container()

        assert splitter1 != container
        assert splitter2 != container

        # hashable
        assert isinstance(splitter1, Hashable)
