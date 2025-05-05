# test_logistic_passive_container.py

from draftsman.entity import (
    LogisticPassiveContainer,
    logistic_passive_containers,
    Container,
)
from draftsman.error import DataFormatError
from draftsman.warning import UnknownEntityWarning, UnknownKeywordWarning

from draftsman.data import mods

from collections.abc import Hashable
import pytest


class TestLogisticPassiveContainer:
    def test_constructor_init(self):
        passive_chest = LogisticPassiveContainer(
            "passive-provider-chest",
            tile_position=[15, 3],
            bar=5,
        )
        assert passive_chest.to_dict() == {
            "name": "passive-provider-chest",
            "position": {"x": 15.5, "y": 3.5},
            "bar": 5,
        }
        passive_chest = LogisticPassiveContainer(
            "passive-provider-chest",
            position={"x": 15.5, "y": 1.5},
            bar=5,
            tags={"A": "B"},
        )
        assert passive_chest.to_dict() == {
            "name": "passive-provider-chest",
            "position": {"x": 15.5, "y": 1.5},
            "bar": 5,
            "tags": {"A": "B"},
        }

        # Warnings
        with pytest.warns(UnknownEntityWarning):
            LogisticPassiveContainer(
                "this is not a logistics passive chest"
            ).validate().reissue_all()

        # Errors
        # Raises schema errors when any of the associated data is incorrect
        with pytest.raises(TypeError):
            LogisticPassiveContainer(
                "passive-provider-chest", id=25
            ).validate().reissue_all()
        with pytest.raises(DataFormatError):
            LogisticPassiveContainer(
                "passive-provider-chest", position=TypeError
            ).validate().reissue_all()
        with pytest.raises(DataFormatError):
            LogisticPassiveContainer(
                "passive-provider-chest", bar="not even trying"
            ).validate().reissue_all()

    def test_power_and_circuit_flags(self):
        for name in logistic_passive_containers:
            container = LogisticPassiveContainer(name)
            assert container.power_connectable == False
            assert container.dual_power_connectable == False
            assert container.circuit_connectable == True
            assert container.dual_circuit_connectable == False

    @pytest.mark.skipif(
        "quality" not in mods.versions, reason="Quality mod not enabled"
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
            chest = LogisticPassiveContainer("passive-provider-chest", quality=quality)
            assert chest.inventory_size == size

    def test_mergable_with(self):
        container1 = LogisticPassiveContainer("passive-provider-chest")
        container2 = LogisticPassiveContainer(
            "passive-provider-chest", bar=10, tags={"some": "stuff"}
        )

        assert container1.mergable_with(container1)

        assert container1.mergable_with(container2)
        assert container2.mergable_with(container1)

        container2.tile_position = (1, 1)
        assert not container1.mergable_with(container2)

    def test_merge(self):
        container1 = LogisticPassiveContainer("passive-provider-chest")
        container2 = LogisticPassiveContainer(
            "passive-provider-chest", bar=10, tags={"some": "stuff"}
        )

        container1.merge(container2)
        del container2

        assert container1.bar == 10
        assert container1.tags == {"some": "stuff"}

    def test_eq(self):
        container1 = LogisticPassiveContainer("passive-provider-chest")
        container2 = LogisticPassiveContainer("passive-provider-chest")

        assert container1 == container2

        container1.tags = {"some": "stuff"}

        assert container1 != container2

        container = Container()

        assert container1 != container
        assert container2 != container

        # hashable
        assert isinstance(container1, Hashable)
