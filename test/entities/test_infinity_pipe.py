# test_infinity_pipe.py
# -*- encoding: utf-8 -*-

from __future__ import unicode_literals

from draftsman.entity import InfinityPipe, infinity_pipes
from draftsman.error import (
    InvalidEntityError,
    InvalidFluidError,
    InvalidModeError,
    DataFormatError,
)
from draftsman.warning import DraftsmanWarning, TemperatureRangeWarning

from schema import SchemaError

import sys
import pytest

if sys.version_info >= (3, 3):  # pragma: no coverage
    import unittest
else:  # pragma: no coverage
    import unittest2 as unittest


class InfinityPipeTesting(unittest.TestCase):
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
                "mode": "at-least",
                "temperature": 500,
            },
        }

        # Warnings
        with pytest.warns(DraftsmanWarning):
            InfinityPipe(unused_keyword="whatever")

        # Errors
        with pytest.raises(InvalidEntityError):
            InfinityPipe("this is not an infinity pipe")
        with pytest.raises(DataFormatError):
            InfinityPipe(infinity_settings={"clearly": "wrong"})

    def test_set_infinity_settings(self):
        pipe = InfinityPipe()
        pipe.infinity_settings = {
            "name": "steam",
            "percentage": 100,
            "mode": "at-least",
            "temperature": 500,
        }
        assert pipe.infinity_settings == {
            "name": "steam",
            "percentage": 100,
            "mode": "at-least",
            "temperature": 500,
        }
        pipe.infinity_settings = None
        assert pipe.infinity_settings == {}
        with pytest.raises(DataFormatError):
            InfinityPipe(infinity_settings={"clearly": "wrong"})

    def test_set_infinite_fluid_settings(self):
        pipe = InfinityPipe()
        pipe.set_infinite_fluid("steam", 100, "at-least", 500)
        assert pipe.infinity_settings == {
            "name": "steam",
            "percentage": 100,
            "mode": "at-least",
            "temperature": 500,
        }

        with pytest.warns(TemperatureRangeWarning):
            pipe.set_infinite_fluid("steam", 1, "at-least", -100)

        with pytest.raises(TypeError):
            pipe.set_infinite_fluid(TypeError)
        with pytest.raises(InvalidFluidError):
            pipe.set_infinite_fluid("incorrect")
        with pytest.raises(TypeError):
            pipe.set_infinite_fluid("steam", "incorrect")
        with pytest.raises(TypeError):
            pipe.set_infinite_fluid("steam", 1, SchemaError)
        with pytest.raises(InvalidModeError):
            pipe.set_infinite_fluid("steam", 1, "incorrect")
        with pytest.raises(TypeError):
            pipe.set_infinite_fluid("steam", 1, "at-least", "incorrect")
        with pytest.raises(ValueError):
            pipe.set_infinite_fluid("steam", -1, "at-least")

    def test_set_infinite_fluid_name(self):
        pipe = InfinityPipe()
        pipe.infinite_fluid_name = "steam"
        assert pipe.infinite_fluid_name == "steam"
        assert pipe.infinity_settings == {"name": "steam"}
        pipe.infinite_fluid_name = None
        assert pipe.infinity_settings == {}
        with pytest.raises(TypeError):
            pipe.infinite_fluid_name = TypeError
        with pytest.raises(InvalidFluidError):
            pipe.infinite_fluid_name = "incorrect"

    def test_set_infinite_fluid_percentage(self):
        pipe = InfinityPipe()
        pipe.infinite_fluid_percentage = 0.5
        assert pipe.infinite_fluid_percentage == 0.5
        assert pipe.infinity_settings == {"percentage": 0.5}
        pipe.infinite_fluid_percentage = None
        assert pipe.infinity_settings == {}
        with pytest.raises(TypeError):
            pipe.infinite_fluid_percentage = TypeError
        with pytest.raises(ValueError):
            pipe.infinite_fluid_percentage = -1

    def test_set_infinite_fluid_mode(self):
        pipe = InfinityPipe()
        pipe.infinite_fluid_mode = "at-most"
        assert pipe.infinite_fluid_mode == "at-most"
        assert pipe.infinity_settings == {"mode": "at-most"}
        pipe.infinite_fluid_mode = None
        assert pipe.infinity_settings == {}
        with pytest.raises(TypeError):
            pipe.infinite_fluid_mode = TypeError
        with pytest.raises(InvalidModeError):
            pipe.infinite_fluid_mode = "incorrect"

    def test_set_infinite_fluid_temperature(self):
        pipe = InfinityPipe()
        pipe.infinite_fluid_temperature = 100
        assert pipe.infinite_fluid_temperature == 100
        assert pipe.infinity_settings == {"temperature": 100}
        pipe.infinite_fluid_temperature = None
        assert pipe.infinity_settings == {}

        with pytest.warns(TemperatureRangeWarning):
            pipe.infinite_fluid_temperature = -100

        with pytest.raises(TypeError):
            pipe.infinite_fluid_temperature = TypeError

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

        assert pipe1.infinity_settings == {
            "name": "steam",
            "percentage": 100,
            "mode": "at-least",
            "temperature": 500,
        }
        assert pipe1.tags == {"some": "stuff"}
