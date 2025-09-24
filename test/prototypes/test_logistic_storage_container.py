# test_logistic_storage_container.py

from draftsman.entity import (
    LogisticStorageContainer,
    logistic_storage_containers,
    Container,
)
from draftsman.error import DataFormatError

# from draftsman.signatures import RequestFilter
from draftsman.warning import UnknownEntityWarning

from collections.abc import Hashable
import pytest


@pytest.fixture
def valid_storage_container():
    return LogisticStorageContainer(
        id="test",
        quality="uncommon",
        tile_position=(1, 1),
        read_contents=False,
        # TODO: request filters or sections?
        # sections=[],
        tags={"blah": "blah"},
    )


class TestLogisticStorageContainer:
    def test_constructor_init(self):
        storage_chest = LogisticStorageContainer(
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
        assert storage_chest.to_dict(version=(1, 0)) == {
            "name": "logistic-chest-storage",
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
        assert storage_chest.to_dict(version=(2, 0)) == {
            "name": "storage-chest",
            "position": {"x": 15.5, "y": 3.5},
            "bar": 5,
        }

        storage_chest = LogisticStorageContainer(
            position=[15.5, 1.5], bar=5, tags={"A": "B"}
        )
        assert storage_chest.to_dict(version=(1, 0)) == {
            "name": "logistic-chest-storage",
            "position": {"x": 15.5, "y": 1.5},
            "bar": 5,
            "tags": {"A": "B"},
        }
        assert storage_chest.to_dict(version=(2, 0)) == {
            "name": "storage-chest",
            "position": {"x": 15.5, "y": 1.5},
            "bar": 5,
            "tags": {"A": "B"},
        }

        # storage_chest = LogisticStorageContainer(item_requests=[("iron-ore", 100)])
        # assert storage_chest.to_dict() == {
        #     "name": "storage-chest",
        #     "position": {"x": 0.5, "y": 0.5},
        #     "request_filters": [{"index": 1, "name": "iron-ore", "count": 100}],
        # }

        # storage_chest = LogisticStorageContainer(
        #     item_requests=[{"index": 1, "name": "iron-ore", "count": 100}]
        # )
        # assert storage_chest.to_dict() == {
        #     "name": "storage-chest",
        #     "position": {"x": 0.5, "y": 0.5},
        #     "request_filters": [{"index": 1, "name": "iron-ore", "count": 100}],
        # }

        # Warnings
        with pytest.warns(UnknownEntityWarning):
            LogisticStorageContainer(
                "this is not a logistics storage chest"
            ).validate().reissue_all()

        # Errors
        # Raises schema errors when any of the associated data is incorrect
        with pytest.raises(TypeError):
            LogisticStorageContainer(id=25).validate().reissue_all()

        with pytest.raises(DataFormatError):
            LogisticStorageContainer(position=TypeError).validate().reissue_all()

        with pytest.raises(DataFormatError):
            LogisticStorageContainer(bar="not even trying").validate().reissue_all()

        with pytest.raises(DataFormatError):
            LogisticStorageContainer(connections="incorrect").validate().reissue_all()

    def test_power_and_circuit_flags(self):
        for name in logistic_storage_containers:
            container = LogisticStorageContainer(name)
            assert container.power_connectable == False
            assert container.dual_power_connectable == False
            assert container.circuit_connectable == True
            assert container.dual_circuit_connectable == False

    def test_mergable_with(self):
        container1 = LogisticStorageContainer()
        container2 = LogisticStorageContainer(
            bar=10,
            # item_requests=[{"name": "utility-science-pack", "index": 1, "count": 0}],
            tags={"some": "stuff"},
        )

        assert container1.mergable_with(container1)

        assert container1.mergable_with(container2)
        assert container2.mergable_with(container1)

        container2.tile_position = (1, 1)
        assert not container1.mergable_with(container2)

    # def test_merge(self):
    #     container1 = LogisticStorageContainer("storage-chest")
    #     container2 = LogisticStorageContainer(
    #         "storage-chest",
    #         bar=10,
    #         request_filters=[{"name": "utility-science-pack", "index": 1, "count": 0}],
    #         tags={"some": "stuff"},
    #     )

    #     container1.merge(container2)
    #     del container2

    #     assert container1.bar == 10
    #     assert container1.request_filters == [
    #         RequestFilter(**{"name": "utility-science-pack", "index": 1, "count": 0})
    #     ]
    #     assert container1.tags == {"some": "stuff"}

    def test_eq(self):
        container1 = LogisticStorageContainer()
        container2 = LogisticStorageContainer()

        assert container1 == container2

        container1.tags = {"some": "stuff"}

        assert container1 != container2

        container = Container()

        assert container1 != container
        assert container2 != container

        # hashable
        assert isinstance(container1, Hashable)
