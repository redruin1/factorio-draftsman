# test_rocket_silo.py

from draftsman.constants import SiloReadMode
from draftsman.entity import RocketSilo, rocket_silos, Container
from draftsman.error import DataFormatError
from draftsman.warning import UnknownEntityWarning, UnknownKeywordWarning

from collections.abc import Hashable
import pytest


class TestRocketSilo:
    def test_constructor_init(self):
        silo = RocketSilo(
            transitional_request_index=12,
            control_behavior={"read_items_mode": SiloReadMode.READ_ORBITAL_REQUESTS},
        )
        assert silo.to_dict() == {
            "name": "rocket-silo",
            "position": {"x": 4.5, "y": 4.5},
            "control_behavior": {"read_items_mode": 2},
            "recipe": "rocket-part",
            "transitional_request_index": 12,
        }

        # Warnings
        with pytest.warns(UnknownKeywordWarning):
            RocketSilo(unused_keyword="whatever").validate().reissue_all()
        with pytest.warns(UnknownEntityWarning):
            RocketSilo("this is not a rocket silo").validate().reissue_all()

        # Errors
        with pytest.raises(DataFormatError):
            RocketSilo(transitional_request_index="incorrect").validate().reissue_all()

    def test_power_and_circuit_flags(self):
        for name in rocket_silos:
            silo = RocketSilo(name)
            assert silo.power_connectable == False
            assert silo.dual_power_connectable == False
            assert silo.circuit_connectable == True
            assert silo.dual_circuit_connectable == False

    def test_mergable_with(self):
        silo1 = RocketSilo("rocket-silo")
        silo2 = RocketSilo("rocket-silo", auto_launch=True, tags={"some": "stuff"})

        assert silo1.mergable_with(silo1)

        assert silo1.mergable_with(silo2)
        assert silo2.mergable_with(silo1)

        silo2.tile_position = (1, 1)
        assert not silo1.mergable_with(silo2)

    def test_merge(self):
        silo1 = RocketSilo("rocket-silo")
        silo2 = RocketSilo(
            "rocket-silo", transitional_request_index=10, tags={"some": "stuff"}
        )

        silo1.merge(silo2)
        del silo2

        # assert silo1.auto_launch == True
        assert silo1.transitional_request_index == 10
        assert silo1.tags == {"some": "stuff"}

    def test_eq(self):
        generator1 = RocketSilo("rocket-silo")
        generator2 = RocketSilo("rocket-silo")

        assert generator1 == generator2

        generator1.tags = {"some": "stuff"}

        assert generator1 != generator2

        container = Container()

        assert generator1 != container
        assert generator2 != container

        # hashable
        assert isinstance(generator1, Hashable)
