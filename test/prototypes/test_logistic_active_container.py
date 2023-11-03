# test_logistic_active_container.py

from draftsman.entity import (
    LogisticActiveContainer,
    logistic_active_containers,
    Container,
)
from draftsman.error import InvalidEntityError, DataFormatError
from draftsman.warning import UnknownEntityWarning, UnknownKeywordWarning

from collections.abc import Hashable
import pytest


class TestContainer:
    def test_constructor_init(self):
        active_chest = LogisticActiveContainer(
            "logistic-chest-active-provider",
            tile_position={"x": 15, "y": 3},
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
        assert active_chest.to_dict() == {
            "name": "logistic-chest-active-provider",
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
        active_chest = LogisticActiveContainer(
            "logistic-chest-active-provider",
            position={"x": 15.5, "y": 1.5},
            bar=5,
            tags={"A": "B"},
        )
        assert active_chest.to_dict() == {
            "name": "logistic-chest-active-provider",
            "position": {"x": 15.5, "y": 1.5},
            "bar": 5,
            "tags": {"A": "B"},
        }
        # Warnings
        with pytest.warns(UnknownKeywordWarning):
            LogisticActiveContainer(
                "logistic-chest-active-provider", position=[0, 0], invalid_keyword="100"
            )
        with pytest.warns(UnknownKeywordWarning):
            LogisticActiveContainer(
                "logistic-chest-active-provider",
                connections={"this is": ["very", "wrong"]},
            )
        with pytest.warns(UnknownEntityWarning):
            LogisticActiveContainer("this is not an active provider chest")

        # Errors
        # Raises schema errors when any of the associated data is incorrect
        with pytest.raises(TypeError):
            LogisticActiveContainer("logistic-chest-active-provider", id=25)

        with pytest.raises(TypeError):
            LogisticActiveContainer(
                "logistic-chest-active-provider", position=TypeError
            )

        with pytest.raises(DataFormatError):
            LogisticActiveContainer(
                "logistic-chest-active-provider", bar="not even trying"
            )

        with pytest.raises(DataFormatError):
            LogisticActiveContainer(
                "logistic-chest-active-provider",
                connections="incorrect",
            )

    def test_power_and_circuit_flags(self):
        for container_name in logistic_active_containers:
            container = LogisticActiveContainer(container_name)
            assert container.power_connectable == False
            assert container.dual_power_connectable == False
            assert container.circuit_connectable == True
            assert container.dual_circuit_connectable == False

    def test_mergable_with(self):
        container1 = LogisticActiveContainer("logistic-chest-active-provider")
        container2 = LogisticActiveContainer(
            "logistic-chest-active-provider", bar=10, tags={"some": "stuff"}
        )

        assert container1.mergable_with(container1)

        assert container1.mergable_with(container2)
        assert container2.mergable_with(container1)

        container2.tile_position = (1, 1)
        assert not container1.mergable_with(container2)

    def test_merge(self):
        container1 = LogisticActiveContainer("logistic-chest-active-provider")
        container2 = LogisticActiveContainer(
            "logistic-chest-active-provider", bar=10, tags={"some": "stuff"}
        )

        container1.merge(container2)
        del container2

        assert container1.bar == 10
        assert container1.tags == {"some": "stuff"}

    def test_eq(self):
        container1 = LogisticActiveContainer("logistic-chest-active-provider")
        container2 = LogisticActiveContainer("logistic-chest-active-provider")

        assert container1 == container2

        container1.tags = {"some": "stuff"}

        assert container1 != container2

        container = Container()

        assert container1 != container
        assert container2 != container

        # hashable
        assert isinstance(container1, Hashable)
