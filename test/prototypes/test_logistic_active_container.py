# test_logistic_active_container.py

from draftsman.entity import (
    LogisticActiveContainer,
    logistic_active_containers,
    Container,
)
from draftsman.error import InvalidEntityError, DataFormatError
from draftsman.warning import UnknownEntityWarning, UnknownKeywordWarning

from draftsman.data import mods

from collections.abc import Hashable
import pytest


class TestContainer:
    def test_constructor_init(self):
        active_chest = LogisticActiveContainer(
            "active-provider-chest",  # "logistic-chest-active-provider",
            tile_position={"x": 15, "y": 3},
            bar=5,
        )
        assert active_chest.to_dict() == {
            "name": "active-provider-chest",
            "position": {"x": 15.5, "y": 3.5},
            "bar": 5,
        }
        active_chest = LogisticActiveContainer(
            "active-provider-chest",
            position={"x": 15.5, "y": 1.5},
            bar=5,
            tags={"A": "B"},
        )
        assert active_chest.to_dict() == {
            "name": "active-provider-chest",
            "position": {"x": 15.5, "y": 1.5},
            "bar": 5,
            "tags": {"A": "B"},
        }
        # Warnings
        with pytest.warns(UnknownEntityWarning):
            LogisticActiveContainer(
                "this is not an active provider chest"
            ).validate().reissue_all()

        # Errors
        # Raises schema errors when any of the associated data is incorrect
        with pytest.raises(TypeError):
            LogisticActiveContainer(
                "active-provider-chest", id=25
            ).validate().reissue_all()

        with pytest.raises(DataFormatError):
            LogisticActiveContainer(
                "active-provider-chest", position=TypeError
            ).validate().reissue_all()

        with pytest.raises(DataFormatError):
            LogisticActiveContainer(
                "active-provider-chest", bar="not even trying"
            ).validate().reissue_all()

    def test_power_and_circuit_flags(self):
        for container_name in logistic_active_containers:
            container = LogisticActiveContainer(container_name)
            assert container.power_connectable == False
            assert container.dual_power_connectable == False
            assert container.circuit_connectable == True
            assert container.dual_circuit_connectable == False

    @pytest.mark.skipif(
        "quality" not in mods.mod_list, reason="Quality mod not enabled"
    )
    def test_quality_inventory_size(self):
        qualities = {
            "normal": 48,
            "uncommon": 62,
            "rare": 76,
            "epic": 91,
            "legendary": 120,
        }
        for quality, size in qualities.items():
            chest = LogisticActiveContainer("active-provider-chest", quality=quality)
            assert chest.inventory_size == size

    def test_mergable_with(self):
        container1 = LogisticActiveContainer("active-provider-chest")
        container2 = LogisticActiveContainer(
            "active-provider-chest", bar=10, tags={"some": "stuff"}
        )

        assert container1.mergable_with(container1)

        assert container1.mergable_with(container2)
        assert container2.mergable_with(container1)

        container2.tile_position = (1, 1)
        assert not container1.mergable_with(container2)

    def test_merge(self):
        container1 = LogisticActiveContainer("active-provider-chest")
        container2 = LogisticActiveContainer(
            "active-provider-chest", bar=10, tags={"some": "stuff"}
        )

        container1.merge(container2)
        del container2

        assert container1.bar == 10
        assert container1.tags == {"some": "stuff"}

    def test_eq(self):
        container1 = LogisticActiveContainer("active-provider-chest")
        container2 = LogisticActiveContainer("active-provider-chest")

        assert container1 == container2

        container1.tags = {"some": "stuff"}

        assert container1 != container2

        container = Container()

        assert container1 != container
        assert container2 != container

        # hashable
        assert isinstance(container1, Hashable)
