# test_infinity_pipe.py

from draftsman.constants import ValidationMode
from draftsman.entity import InfinityPipe, infinity_pipes, Container
from draftsman.error import DataFormatError
import draftsman.validators
from draftsman.warning import (
    UnknownEntityWarning,
    UnknownFluidWarning,
    UnknownKeywordWarning,
)

from collections.abc import Hashable
import pytest


@pytest.fixture
def valid_infinity_pipe():
    if len(infinity_pipes) == 0:
        return None
    return InfinityPipe(
        "infinity-pipe",
        id="test",
        quality="uncommon",
        tile_position=(1, 1),
        fluid_name="steam",
        percentage=0.5,
        mode="at-most",
        temperature=500,
        tags={"blah": "blah"},
    )


class TestInfinityPipe:
    def test_constructor_init(self):
        pipe = InfinityPipe(
            fluid_name="steam",
            percentage=1.0,
            mode="at-least",
            temperature=500,
        )
        assert pipe.to_dict() == {
            "name": "infinity-pipe",
            "position": {"x": 0.5, "y": 0.5},
            "infinity_settings": {
                "name": "steam",
                "percentage": 1.0,
                # "mode": "at-least", # Default
                "temperature": 500,
            },
        }

        # Warnings
        with pytest.warns(UnknownEntityWarning):
            InfinityPipe("this is not an infinity pipe").validate().reissue_all()

        # Errors
        with pytest.raises(DataFormatError):
            InfinityPipe(tags="incorrect").validate().reissue_all()

    def test_set_infinite_fluid(self):
        pipe = InfinityPipe()
        pipe.set_infinite_fluid("steam", 1.0, "at-least", 500)
        assert pipe.fluid_name == "steam"
        assert pipe.percentage == 1.0
        assert pipe.mode == "at-least"
        assert pipe.temperature == 500

        with pytest.raises(DataFormatError):
            pipe.set_infinite_fluid("steam", 1, "at-least", -100)

        with pytest.raises(DataFormatError):
            pipe.set_infinite_fluid(TypeError)
        # with pytest.raises(DataFormatError): # TODO
        #     pipe.set_infinite_fluid("incorrect")
        with pytest.raises(DataFormatError):
            pipe.set_infinite_fluid("steam", "incorrect")
        with pytest.raises(DataFormatError):
            pipe.set_infinite_fluid("steam", 1, TypeError)
        with pytest.raises(DataFormatError):
            pipe.set_infinite_fluid("steam", 1, "incorrect")
        with pytest.raises(DataFormatError):
            pipe.set_infinite_fluid("steam", 1, "at-least", "incorrect")
        with pytest.raises(DataFormatError):
            pipe.set_infinite_fluid("steam", -1, "at-least")

    def test_set_fluid_name(self):
        pipe = InfinityPipe()
        pipe.fluid_name = "steam"
        assert pipe.fluid_name == "steam"

        pipe.fluid_name = None
        assert pipe.fluid_name == None

        with pytest.warns(UnknownFluidWarning):
            pipe.fluid_name = "incorrect"

        with pytest.raises(DataFormatError):
            pipe.fluid_name = TypeError

        with draftsman.validators.set_mode(ValidationMode.DISABLED):
            pipe.fluid_name = False
            assert pipe.fluid_name == False
            assert pipe.to_dict() == {
                "name": "infinity-pipe",
                "position": {"x": 0.5, "y": 0.5},
                "infinity_settings": {"name": False},
            }

    def test_set_percentage(self):
        pipe = InfinityPipe()
        pipe.percentage = 0.5
        assert pipe.percentage == 0.5

        with pytest.raises(DataFormatError):
            pipe.percentage = TypeError
        with pytest.raises(DataFormatError):
            pipe.percentage = -1

        with draftsman.validators.set_mode(ValidationMode.DISABLED):
            pipe.percentage = -1
            assert pipe.percentage == -1
            assert pipe.to_dict() == {
                "name": "infinity-pipe",
                "position": {"x": 0.5, "y": 0.5},
                "infinity_settings": {"percentage": -1},
            }

    def test_set_mode(self):
        pipe = InfinityPipe("infinity-pipe")
        assert pipe.mode == "at-least"

        pipe.mode = "at-most"
        assert pipe.mode == "at-most"

        with pytest.raises(DataFormatError):
            pipe.mode = TypeError
        with pytest.raises(DataFormatError):
            pipe.mode = "incorrect"

        with draftsman.validators.set_mode(ValidationMode.DISABLED):
            pipe.mode = "incorrect"
            assert pipe.mode == "incorrect"
            assert pipe.to_dict() == {
                "name": "infinity-pipe",
                "position": {"x": 0.5, "y": 0.5},
                "infinity_settings": {"mode": "incorrect"},
            }

    def test_set_temperature(self):
        pipe = InfinityPipe("infinity-pipe")
        # # Cannot be set when 'name' is None
        # with pytest.raises(DataFormatError):
        #     pipe.temperature = 200

        pipe.fluid_name = "steam"
        pipe.temperature = 200
        assert pipe.fluid_name == "steam"
        assert pipe.temperature == 200

        # Swapping to water will make the value exceed its maximum temperature
        # TODO: reimplement
        # with pytest.raises(DataFormatError):
        #     pipe.fluid_name = "water"
        # assert pipe.fluid_name == "water"
        # assert pipe.temperature == 200

        # Swapping to an unknown fluid name should issue no temperature warning,
        # but a warning about the unrecognized name instead
        with pytest.warns(UnknownFluidWarning):
            pipe.fluid_name = "wrong"
        assert pipe.fluid_name == "wrong"
        assert pipe.temperature == 200

        # removing temperature should have no effect
        pipe.fluid_name = None
        assert pipe.temperature == 200

        with pytest.raises(DataFormatError):
            pipe.temperature = TypeError

        pipe = InfinityPipe("infinity-pipe")

        with draftsman.validators.set_mode(ValidationMode.DISABLED):
            pipe.temperature = "incorrect"
            assert pipe.temperature == "incorrect"
            assert pipe.to_dict() == {
                "name": "infinity-pipe",
                "position": {"x": 0.5, "y": 0.5},
                "infinity_settings": {"temperature": "incorrect"},
            }

    def test_mergable_with(self):
        pipe1 = InfinityPipe("infinity-pipe")
        pipe2 = InfinityPipe(
            "infinity-pipe",
            fluid_name="steam",
            percentage=100,
            mode="at-least",
            temperature=500,
            tags={"some": "stuff"},
        )

        assert pipe1.mergable_with(pipe1)

        assert pipe1.mergable_with(pipe2)
        assert pipe2.mergable_with(pipe1)

        pipe2.tile_position = (1, 1)
        assert not pipe1.mergable_with(pipe2)

    def test_merge(self):
        pipe1 = InfinityPipe("infinity-pipe")
        pipe2 = InfinityPipe(
            "infinity-pipe",
            fluid_name="steam",
            percentage=100.0,
            mode="at-least",
            temperature=500,
            tags={"some": "stuff"},
        )

        pipe1.merge(pipe2)
        del pipe2

        assert pipe1.fluid_name == "steam"
        assert pipe1.percentage == 100
        assert pipe1.mode == "at-least"
        assert pipe1.temperature == 500
        assert pipe1.tags == {"some": "stuff"}

    def test_eq(self):
        pipe1 = InfinityPipe("infinity-pipe")
        pipe2 = InfinityPipe("infinity-pipe")

        assert pipe1 == pipe2

        pipe1.tags = {"some": "stuff"}

        assert pipe1 != pipe2

        container = Container()

        assert pipe1 != container
        assert pipe2 != container

        # hashable
        assert isinstance(pipe1, Hashable)
