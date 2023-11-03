# test_logistic_request_container.py

from draftsman.entity import (
    LogisticRequestContainer,
    logistic_request_containers,
    Container,
)
from draftsman.error import DataFormatError
from draftsman.signatures import RequestFilters
from draftsman.warning import UnknownEntityWarning, UnknownKeywordWarning

from collections.abc import Hashable
import pytest


class TestLogisticRequestContainer:
    def test_constructor_init(self):
        request_chest = LogisticRequestContainer(
            "logistic-chest-requester",
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
        assert request_chest.to_dict() == {
            "name": "logistic-chest-requester",
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
        request_chest = LogisticRequestContainer(
            "logistic-chest-requester",
            position={"x": 15.5, "y": 1.5},
            bar=5,
            tags={"A": "B"},
        )
        assert request_chest.to_dict() == {
            "name": "logistic-chest-requester",
            "position": {"x": 15.5, "y": 1.5},
            "bar": 5,
            "tags": {"A": "B"},
        }

        request_chest = LogisticRequestContainer(
            request_from_buffers=True, request_filters=[("iron-ore", 100)]
        )
        assert request_chest.to_dict() == {
            "name": "logistic-chest-requester",
            "position": {"x": 0.5, "y": 0.5},
            "request_from_buffers": True,
            "request_filters": [{"index": 1, "name": "iron-ore", "count": 100}],
        }

        request_chest = LogisticRequestContainer(
            request_filters=[{"index": 1, "name": "iron-ore", "count": 100}]
        )
        assert request_chest.to_dict() == {
            "name": "logistic-chest-requester",
            "position": {"x": 0.5, "y": 0.5},
            "request_filters": [{"index": 1, "name": "iron-ore", "count": 100}],
        }

        # Warnings
        with pytest.warns(UnknownKeywordWarning):
            LogisticRequestContainer(
                "logistic-chest-requester", position=[0, 0], invalid_keyword="100"
            )
        with pytest.warns(UnknownKeywordWarning):
            LogisticRequestContainer(control_behavior={"unused_key": "something"})
        with pytest.warns(UnknownEntityWarning):
            LogisticRequestContainer("this is not a logistics storage chest")

        # Errors
        # Raises schema errors when any of the associated data is incorrect
        with pytest.raises(TypeError):
            LogisticRequestContainer("logistic-chest-requester", id=25)
        with pytest.raises(TypeError):
            LogisticRequestContainer("logistic-chest-requester", position=TypeError)
        with pytest.raises(DataFormatError):
            LogisticRequestContainer("logistic-chest-requester", bar="not even trying")
        with pytest.raises(DataFormatError):
            LogisticRequestContainer(
                "logistic-chest-requester", connections="incorrect"
            )
        with pytest.raises(DataFormatError):
            LogisticRequestContainer(
                "logistic-chest-requester",
                request_filters={"this is": ["very", "wrong"]},
            )
        with pytest.raises(DataFormatError):
            LogisticRequestContainer(
                "logistic-chest-requester", request_from_buffers="invalid"
            )
        with pytest.raises(DataFormatError):
            LogisticRequestContainer(control_behavior="incorrect")

    def test_power_and_circuit_flags(self):
        for name in logistic_request_containers:
            container = LogisticRequestContainer(name)
            assert container.power_connectable == False
            assert container.dual_power_connectable == False
            assert container.circuit_connectable == True
            assert container.dual_circuit_connectable == False

    def test_mergable_with(self):
        container1 = LogisticRequestContainer("logistic-chest-requester")
        container2 = LogisticRequestContainer(
            "logistic-chest-requester",
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
        container1 = LogisticRequestContainer("logistic-chest-requester")
        container2 = LogisticRequestContainer(
            "logistic-chest-requester",
            bar=10,
            request_filters=[{"name": "utility-science-pack", "index": 1, "count": 10}],
            tags={"some": "stuff"},
        )

        container1.merge(container2)
        del container2

        assert container1.bar == 10
        assert container1.request_filters == RequestFilters(root=[
            {"name": "utility-science-pack", "index": 1, "count": 10}
        ])
        assert container1.tags == {"some": "stuff"}

    def test_eq(self):
        container1 = LogisticRequestContainer("logistic-chest-requester")
        container2 = LogisticRequestContainer("logistic-chest-requester")

        assert container1 == container2

        container1.tags = {"some": "stuff"}

        assert container1 != container2

        container = Container()

        assert container1 != container
        assert container2 != container

        # hashable
        assert isinstance(container1, Hashable)
