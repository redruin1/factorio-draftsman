# test_radar.py

from draftsman.entity import Radar, Container
from draftsman.warning import UnknownEntityWarning, UnknownKeywordWarning

from collections.abc import Hashable
import pytest


@pytest.fixture
def valid_radar():
    return Radar(
        "radar",
        id="test",
        quality="uncommon",
        tile_position=(1, 1),
        tags={"blah": "blah"},
    )


class TestRadar:
    def test_contstructor_init(self):
        radar = Radar()

        with pytest.warns(UnknownKeywordWarning):
            Radar.from_dict(
                {"name": "radar", "unused_keyword": "whatever"}
            ).validate().reissue_all()

        with pytest.warns(UnknownEntityWarning):
            Radar("this is not a radar").validate().reissue_all()

    def test_mergable_with(self):
        radar1 = Radar("radar")
        radar2 = Radar("radar", tags={"some": "stuff"})

        assert radar1.mergable_with(radar1)

        assert radar1.mergable_with(radar2)
        assert radar2.mergable_with(radar1)

        radar2.tile_position = (1, 1)
        assert not radar1.mergable_with(radar2)

    def test_merge(self):
        radar1 = Radar("radar")
        radar2 = Radar("radar", tags={"some": "stuff"})

        radar1.merge(radar2)
        del radar2

        assert radar1.tags == {"some": "stuff"}

    def test_eq(self):
        radar1 = Radar("radar")
        radar2 = Radar("radar")

        assert radar1 == radar2

        radar1.tags = {"some": "stuff"}

        assert radar1 != radar2

        container = Container()

        assert radar1 != container
        assert radar2 != container

        # hashable
        assert isinstance(radar1, Hashable)
