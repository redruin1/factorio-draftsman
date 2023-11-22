# test_infinity_pipe.py

from draftsman.constants import ValidationMode
from draftsman.entity import InfinityPipe, infinity_pipes, Container
from draftsman.error import DataFormatError
from draftsman.warning import (
    UnknownEntityWarning,
    UnknownFluidWarning,
    UnknownKeywordWarning,
)

from collections.abc import Hashable
import pytest


class TestInfinityPipe:
    def test_constructor_init(self):
        pipe = InfinityPipe(
            infinity_settings={
                "name": "steam",
                "percentage": 100,
                "mode": "at-least",
                "temperature": 500,
            }
        )
        assert pipe.to_dict() == {
            "name": "infinity-pipe",
            "position": {"x": 0.5, "y": 0.5},
            "infinity_settings": {
                "name": "steam",
                "percentage": 100,
                # "mode": "at-least", # Default
                "temperature": 500,
            },
        }

        # Warnings
        with pytest.warns(UnknownKeywordWarning):
            InfinityPipe(unused_keyword="whatever")
        with pytest.warns(UnknownKeywordWarning):
            InfinityPipe(infinity_settings={"clearly": "wrong"})
        with pytest.warns(UnknownEntityWarning):
            InfinityPipe("this is not an infinity pipe")

        # Errors
        with pytest.raises(DataFormatError):
            InfinityPipe(infinity_settings="incorrect")

    def test_set_infinity_settings(self):
        pipe = InfinityPipe()
        pipe.infinity_settings = {
            "name": "steam",
            "percentage": 100,
            "mode": "at-least",
            "temperature": 500,
        }
        assert pipe.infinity_settings == InfinityPipe.Format.InfinitySettings(
            **{
                "name": "steam",
                "percentage": 100,
                "mode": "at-least",
                "temperature": 500,
            }
        )

        pipe.infinity_settings = None
        assert pipe.infinity_settings == None

        # Warnings
        with pytest.warns(UnknownKeywordWarning):
            pipe.infinity_settings = {"clearly": "wrong"}

        # Errors
        with pytest.raises(DataFormatError):
            pipe.infinity_settings = "incorrect"

    def test_set_infinite_fluid(self):
        pipe = InfinityPipe()
        pipe.set_infinite_fluid("steam", 1.0, "at-least", 500)
        assert pipe.infinity_settings == InfinityPipe.Format.InfinitySettings(
            **{
                "name": "steam",
                "percentage": 1.0,
                "mode": "at-least",
                "temperature": 500,
            }
        )

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

    def test_set_infinite_fluid_name(self):
        pipe = InfinityPipe()
        pipe.infinite_fluid_name = "steam"
        assert pipe.infinite_fluid_name == "steam"

        pipe.infinite_fluid_name = None
        assert pipe.infinite_fluid_name == None

        with pytest.warns(UnknownFluidWarning):
            pipe.infinite_fluid_name = "incorrect"

        with pytest.raises(DataFormatError):
            pipe.infinite_fluid_name = TypeError

        pipe.validate_assignment = "none"
        assert pipe.validate_assignment == ValidationMode.NONE

        pipe.infinite_fluid_name = False
        assert pipe.infinite_fluid_name == False
        assert pipe.to_dict() == {
            "name": "infinity-pipe",
            "position": {"x": 0.5, "y": 0.5},
            "infinity_settings": {"name": False},
        }

    def test_set_infinite_fluid_percentage(self):
        pipe = InfinityPipe()
        pipe.infinite_fluid_percentage = 0.5
        assert pipe.infinite_fluid_percentage == 0.5

        pipe.infinite_fluid_percentage = None
        assert pipe.infinite_fluid_percentage == None

        with pytest.raises(DataFormatError):
            pipe.infinite_fluid_percentage = TypeError
        with pytest.raises(DataFormatError):
            pipe.infinite_fluid_percentage = -1

        pipe.validate_assignment = "none"
        assert pipe.validate_assignment == ValidationMode.NONE

        pipe.infinite_fluid_percentage = -1
        assert pipe.infinite_fluid_percentage == -1
        assert pipe.to_dict() == {
            "name": "infinity-pipe",
            "position": {"x": 0.5, "y": 0.5},
            "infinity_settings": {"percentage": -1},
        }

    def test_set_infinite_fluid_mode(self):
        pipe = InfinityPipe()
        pipe.infinite_fluid_mode = "at-most"
        assert pipe.infinite_fluid_mode == "at-most"

        pipe.infinite_fluid_mode = None
        assert pipe.infinite_fluid_mode == None

        with pytest.raises(DataFormatError):
            pipe.infinite_fluid_mode = TypeError
        with pytest.raises(DataFormatError):
            pipe.infinite_fluid_mode = "incorrect"

        pipe.validate_assignment = "none"
        assert pipe.validate_assignment == ValidationMode.NONE

        pipe.infinite_fluid_mode = "incorrect"
        assert pipe.infinite_fluid_mode == "incorrect"
        assert pipe.to_dict() == {
            "name": "infinity-pipe",
            "position": {"x": 0.5, "y": 0.5},
            "infinity_settings": {"mode": "incorrect"},
        }

    def test_set_infinite_fluid_temperature(self):
        pipe = InfinityPipe("infinity-pipe")
        # Cannot be set when 'name' is None
        with pytest.raises(DataFormatError):
            pipe.infinite_fluid_temperature = 200

        pipe.infinite_fluid_name = "steam"
        pipe.infinite_fluid_temperature = 200
        assert pipe.infinite_fluid_name == "steam"
        assert pipe.infinite_fluid_temperature == 200

        # Swapping to water will make the value exceed its maximum temperature
        with pytest.raises(DataFormatError):
            pipe.infinite_fluid_name = "water"
        assert pipe.infinite_fluid_name == "water"
        assert pipe.infinite_fluid_temperature == 200

        # Swapping to an unknown fluid name should issue no temperature warning,
        # but a warning about the unrecognized name instead
        with pytest.warns(UnknownFluidWarning):
            pipe.infinite_fluid_name = "wrong"
        assert pipe.infinite_fluid_name == "wrong"
        assert pipe.infinite_fluid_temperature == 200

        # removing temperature should have no effect
        pipe.infinite_fluid_temperature = None
        assert pipe.infinite_fluid_temperature == None

        with pytest.raises(DataFormatError):
            pipe.infinite_fluid_temperature = TypeError

        pipe = InfinityPipe("infinity-pipe")

        pipe.validate_assignment = "none"
        assert pipe.validate_assignment == ValidationMode.NONE

        pipe.infinite_fluid_temperature = "incorrect"
        assert pipe.infinite_fluid_temperature == "incorrect"
        assert pipe.to_dict() == {
            "name": "infinity-pipe",
            "position": {"x": 0.5, "y": 0.5},
            "infinity_settings": {"temperature": "incorrect"},
        }

    def test_mergable_with(self):
        pipe1 = InfinityPipe("infinity-pipe")
        pipe2 = InfinityPipe(
            "infinity-pipe",
            infinity_settings={
                "name": "steam",
                "percentage": 100,
                "mode": "at-least",
                "temperature": 500,
            },
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
            infinity_settings={
                "name": "steam",
                "percentage": 100,
                "mode": "at-least",
                "temperature": 500,
            },
            tags={"some": "stuff"},
        )

        pipe1.merge(pipe2)
        del pipe2

        assert pipe1.infinity_settings == InfinityPipe.Format.InfinitySettings(
            **{
                "name": "steam",
                "percentage": 100,
                "mode": "at-least",
                "temperature": 500,
            }
        )
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
