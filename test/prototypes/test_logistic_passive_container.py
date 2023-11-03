# test_logistic_passive_container.py

from draftsman.entity import (
    LogisticPassiveContainer,
    logistic_passive_containers,
    Container,
)
from draftsman.error import DataFormatError
from draftsman.warning import UnknownEntityWarning, UnknownKeywordWarning

from collections.abc import Hashable
import pytest


class TestLogisticPassiveContainer:
    def test_constructor_init(self):
        passive_chest = LogisticPassiveContainer(
            "logistic-chest-passive-provider",
            tile_position=[15, 3],
            bar=5,
            connections={
                "1": {
                    "red": [
                        {"entity_id": 2},
                        {"entity_id": 2, "circuit_id": 1},
                    ]
                }
            },
        )
        assert passive_chest.to_dict() == {
            "name": "logistic-chest-passive-provider",
            "position": {"x": 15.5, "y": 3.5},
            "bar": 5,
            "connections": {
                "1": {
                    "red": [
                        {"entity_id": 2},
                        {"entity_id": 2, "circuit_id": 1},
                    ]
                }
            },
        }
        passive_chest = LogisticPassiveContainer(
            "logistic-chest-passive-provider",
            position={"x": 15.5, "y": 1.5},
            bar=5,
            tags={"A": "B"},
        )
        assert passive_chest.to_dict() == {
            "name": "logistic-chest-passive-provider",
            "position": {"x": 15.5, "y": 1.5},
            "bar": 5,
            "tags": {"A": "B"},
        }

        # Warnings
        with pytest.warns(UnknownKeywordWarning):
            LogisticPassiveContainer(
                "logistic-chest-passive-provider",
                position=[0, 0],
                invalid_keyword="100",
            )
        with pytest.warns(UnknownEntityWarning):
            LogisticPassiveContainer("this is not a logistics passive chest")

        # Errors
        # Raises schema errors when any of the associated data is incorrect
        with pytest.raises(TypeError):
            LogisticPassiveContainer("logistic-chest-passive-provider", id=25)
        with pytest.raises(TypeError):
            LogisticPassiveContainer(
                "logistic-chest-passive-provider", position=TypeError
            )
        with pytest.raises(DataFormatError):
            LogisticPassiveContainer(
                "logistic-chest-passive-provider", bar="not even trying"
            )
        with pytest.raises(DataFormatError):
            LogisticPassiveContainer(
                "logistic-chest-passive-provider",
                connections="incorrect",
            )

    def test_power_and_circuit_flags(self):
        for name in logistic_passive_containers:
            container = LogisticPassiveContainer(name)
            assert container.power_connectable == False
            assert container.dual_power_connectable == False
            assert container.circuit_connectable == True
            assert container.dual_circuit_connectable == False

    def test_mergable_with(self):
        container1 = LogisticPassiveContainer("logistic-chest-passive-provider")
        container2 = LogisticPassiveContainer(
            "logistic-chest-passive-provider", bar=10, tags={"some": "stuff"}
        )

        assert container1.mergable_with(container1)

        assert container1.mergable_with(container2)
        assert container2.mergable_with(container1)

        container2.tile_position = (1, 1)
        assert not container1.mergable_with(container2)

    def test_merge(self):
        container1 = LogisticPassiveContainer("logistic-chest-passive-provider")
        container2 = LogisticPassiveContainer(
            "logistic-chest-passive-provider", bar=10, tags={"some": "stuff"}
        )

        container1.merge(container2)
        del container2

        assert container1.bar == 10
        assert container1.tags == {"some": "stuff"}

    def test_eq(self):
        container1 = LogisticPassiveContainer("logistic-chest-passive-provider")
        container2 = LogisticPassiveContainer("logistic-chest-passive-provider")

        assert container1 == container2

        container1.tags = {"some": "stuff"}

        assert container1 != container2

        container = Container()

        assert container1 != container
        assert container2 != container

        # hashable
        assert isinstance(container1, Hashable)
