# test_logistic_buffer_container.py

from draftsman.entity import (
    LogisticBufferContainer,
    logistic_buffer_containers,
    Container,
)
from draftsman.error import DataFormatError
from draftsman.signatures import RequestFilter
from draftsman.warning import UnknownEntityWarning, UnknownKeywordWarning

from collections.abc import Hashable
import pytest


class TestLogisticBufferContainer:
    def test_constructor_init(self):
        buffer_chest = LogisticBufferContainer(
            "logistic-chest-buffer",
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
        assert buffer_chest.to_dict() == {
            "name": "logistic-chest-buffer",
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
        buffer_chest = LogisticBufferContainer(
            "logistic-chest-buffer",
            position={"x": 15.5, "y": 1.5},
            bar=5,
            tags={"A": "B"},
        )
        assert buffer_chest.to_dict() == {
            "name": "logistic-chest-buffer",
            "position": {"x": 15.5, "y": 1.5},
            "bar": 5,
            "tags": {"A": "B"},
        }

        buffer_chest = LogisticBufferContainer(request_filters=[("iron-ore", 100)])
        assert buffer_chest.to_dict() == {
            "name": "logistic-chest-buffer",
            "position": {"x": 0.5, "y": 0.5},
            "request_filters": [{"index": 1, "name": "iron-ore", "count": 100}],
        }

        buffer_chest = LogisticBufferContainer(
            request_filters=[{"index": 1, "name": "iron-ore", "count": 100}]
        )
        assert buffer_chest.to_dict() == {
            "name": "logistic-chest-buffer",
            "position": {"x": 0.5, "y": 0.5},
            "request_filters": [{"index": 1, "name": "iron-ore", "count": 100}],
        }

        # Warnings
        with pytest.warns(UnknownKeywordWarning):
            LogisticBufferContainer(
                "logistic-chest-buffer", position=[0, 0], invalid_keyword="100"
            )
        with pytest.warns(UnknownKeywordWarning):
            LogisticBufferContainer(control_behavior={"unused_key": "something"})
        with pytest.warns(UnknownEntityWarning):
            LogisticBufferContainer("this is not a logistics storage chest")

        # Errors
        # Raises schema errors when any of the associated data is incorrect
        with pytest.raises(TypeError):
            LogisticBufferContainer("logistic-chest-buffer", id=25)
        with pytest.raises(TypeError):
            LogisticBufferContainer("logistic-chest-buffer", position=TypeError)
        with pytest.raises(DataFormatError):
            LogisticBufferContainer("logistic-chest-buffer", bar="not even trying")
        with pytest.raises(DataFormatError):
            LogisticBufferContainer("logistic-chest-buffer", connections="incorrect")
        with pytest.raises(DataFormatError):
            LogisticBufferContainer(
                "logistic-chest-buffer", request_filters={"this is": ["very", "wrong"]}
            )
        with pytest.raises(DataFormatError):
            LogisticBufferContainer(control_behavior="incorrect")

    def test_power_and_circuit_flags(self):
        for name in logistic_buffer_containers:
            container = LogisticBufferContainer(name)
            assert container.power_connectable == False
            assert container.dual_power_connectable == False
            assert container.circuit_connectable == True
            assert container.dual_circuit_connectable == False

    def test_mergable_with(self):
        container1 = LogisticBufferContainer("logistic-chest-buffer")
        container2 = LogisticBufferContainer(
            "logistic-chest-buffer",
            bar=10,
            request_filters=[{"name": "utility-science-pack", "index": 1, "count": 10}],
            tags={"some": "stuff"},
        )

        assert container1.mergable_with(container1)

        assert container1.mergable_with(container2)
        assert container2.mergable_with(container1)

        container2.tile_position = (1, 1)
        assert not container1.mergable_with(container2)

    def test_merge(self):
        container1 = LogisticBufferContainer("logistic-chest-buffer")
        container2 = LogisticBufferContainer(
            "logistic-chest-buffer",
            bar=10,
            request_filters=[{"name": "utility-science-pack", "index": 1, "count": 10}],
            tags={"some": "stuff"},
        )

        container1.merge(container2)
        del container2

        assert container1.bar == 10
        assert container1.request_filters == [
            RequestFilter(**{"name": "utility-science-pack", "index": 1, "count": 10})
        ]
        assert container1.tags == {"some": "stuff"}

    def test_eq(self):
        container1 = LogisticBufferContainer("logistic-chest-buffer")
        container2 = LogisticBufferContainer("logistic-chest-buffer")

        assert container1 == container2

        container1.tags = {"some": "stuff"}

        assert container1 != container2

        container = Container()

        assert container1 != container
        assert container2 != container

        # hashable
        assert isinstance(container1, Hashable)
