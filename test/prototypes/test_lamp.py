# test_lamp.py

from draftsman.constants import LampColorMode, ValidationMode
from draftsman.entity import Lamp, lamps, Container
from draftsman.error import DataFormatError
import draftsman.validators
from draftsman.warning import UnknownEntityWarning, UnknownKeywordWarning

from collections.abc import Hashable
import pytest


@pytest.fixture
def valid_lamp():
    if len(lamps) == 0:
        return None
    return Lamp(
        "small-lamp",
        id="test",
        quality="uncommon",
        tile_position=(1, 1),
        color=(0.5, 0.5, 0.5),
        always_on=True,
        use_colors=True,
        color_mode=LampColorMode.PACKED_RGB,
        tags={"blah": "blah"},
    )


class TestLamp:
    def test_constructor_init(self):
        lamp = Lamp("small-lamp", use_colors=True)
        assert lamp.to_dict() == {
            "name": "small-lamp",
            "position": {"x": 0.5, "y": 0.5},
            "control_behavior": {"use_colors": True},
        }

        # Warnings
        with pytest.warns(UnknownEntityWarning):
            Lamp("this is not a lamp").validate().reissue_all()

        # Errors
        with pytest.raises(DataFormatError):
            Lamp(tags="incorrect").validate().reissue_all()

    def test_set_use_colors(self):
        lamp = Lamp("small-lamp")
        assert lamp.use_colors == False

        lamp.use_colors = True
        assert lamp.use_colors == True

        with pytest.raises(DataFormatError):
            lamp.use_colors = "incorrect"

        with draftsman.validators.set_mode(ValidationMode.DISABLED):
            lamp.use_colors = "incorrect"
            assert lamp.use_colors == "incorrect"
            assert lamp.to_dict() == {
                "name": "small-lamp",
                "position": {"x": 0.5, "y": 0.5},
                "control_behavior": {"use_colors": "incorrect"},
            }

    def test_mergable_with(self):
        lamp1 = Lamp("small-lamp")
        lamp2 = Lamp("small-lamp", use_colors=True, tags={"some": "stuff"})

        assert lamp1.mergable_with(lamp1)

        assert lamp1.mergable_with(lamp2)
        assert lamp2.mergable_with(lamp1)

        lamp2.tile_position = (1, 1)
        assert not lamp1.mergable_with(lamp2)

    def test_merge(self):
        lamp1 = Lamp("small-lamp")
        lamp2 = Lamp("small-lamp", use_colors=True, tags={"some": "stuff"})

        lamp1.merge(lamp2)
        del lamp2

        assert lamp1.use_colors == True
        assert lamp1.tags == {"some": "stuff"}

    def test_eq(self):
        lamp1 = Lamp("small-lamp")
        lamp2 = Lamp("small-lamp")

        assert lamp1 == lamp2

        lamp1.tags = {"some": "stuff"}

        assert lamp1 != lamp2

        container = Container()

        assert lamp1 != container
        assert lamp2 != container

        # hashable
        assert isinstance(lamp1, Hashable)
