# test_logistic_buffer_container.py

from draftsman.entity import (
    LogisticBufferContainer,
    logistic_buffer_containers,
    Container,
)
from draftsman.error import DataFormatError
from draftsman.classes.mixins import RequestFiltersMixin
from draftsman.signatures import RequestFilter, Section
from draftsman.warning import UnknownEntityWarning, UnknownKeywordWarning

from draftsman.data import mods

from collections.abc import Hashable
import pytest


class TestLogisticBufferContainer:
    def test_constructor_init(self):
        buffer_chest = LogisticBufferContainer(
            "buffer-chest",
            tile_position=[15, 3],
            bar=5,
        )
        assert buffer_chest.to_dict() == {
            "name": "buffer-chest",
            "position": {"x": 15.5, "y": 3.5},
            "bar": 5,
        }
        buffer_chest = LogisticBufferContainer(
            "buffer-chest",
            position={"x": 15.5, "y": 1.5},
            bar=5,
            tags={"A": "B"},
        )
        assert buffer_chest.to_dict() == {
            "name": "buffer-chest",
            "position": {"x": 15.5, "y": 1.5},
            "bar": 5,
            "tags": {"A": "B"},
        }

        buffer_chest = LogisticBufferContainer(request_filters=[("iron-ore", 100)])
        assert buffer_chest.to_dict() == {
            "name": "buffer-chest",
            "position": {"x": 0.5, "y": 0.5},
            "request_filters": [("iron-ore", 100)],
        }

        buffer_chest = LogisticBufferContainer(
            request_filters=[{"index": 1, "name": "iron-ore", "count": 100}]
        )
        assert buffer_chest.to_dict() == {
            "name": "buffer-chest",
            "position": {"x": 0.5, "y": 0.5},
            "request_filters": [{"index": 1, "name": "iron-ore", "count": 100}],
        }

        # Warnings
        with pytest.warns(UnknownKeywordWarning):
            LogisticBufferContainer(
                "buffer-chest", position=[0, 0], invalid_keyword="100"
            ).validate().reissue_all()
        with pytest.warns(UnknownKeywordWarning):
            LogisticBufferContainer(control_behavior={"unused_key": "something"}).validate().reissue_all()
        with pytest.warns(UnknownEntityWarning):
            LogisticBufferContainer("this is not a buffer chest").validate().reissue_all()

        # Errors
        # Raises schema errors when any of the associated data is incorrect
        with pytest.raises(TypeError):
            LogisticBufferContainer("buffer-chest", id=25).validate().reissue_all()
        with pytest.raises(TypeError):
            LogisticBufferContainer("buffer-chest", position=TypeError).validate().reissue_all()
        with pytest.raises(DataFormatError):
            LogisticBufferContainer("buffer-chest", bar="not even trying").validate().reissue_all()
        with pytest.raises(DataFormatError):
            LogisticBufferContainer(
                "buffer-chest", request_filters=["very", "wrong"]
            ).validate().reissue_all()
        with pytest.raises(DataFormatError):
            LogisticBufferContainer("buffer-chest", control_behavior="incorrect").validate().reissue_all()

    def test_power_and_circuit_flags(self):
        for name in logistic_buffer_containers:
            container = LogisticBufferContainer(name)
            assert container.power_connectable == False
            assert container.dual_power_connectable == False
            assert container.circuit_connectable == True
            assert container.dual_circuit_connectable == False

    @pytest.mark.skipif("quality" not in mods.mod_list, reason="Quality mod not enabled")
    def test_quality_inventory_size(self):
        qualities = {
            "normal": 48,
            "uncommon": 62,
            "rare": 76,
            "epic": 91,
            "legendary": 120
        }
        for quality, size in qualities.items():
            chest = LogisticBufferContainer("buffer-chest", quality=quality)
            assert chest.inventory_size == size

    def test_mergable_with(self):
        container1 = LogisticBufferContainer("buffer-chest")
        container2 = LogisticBufferContainer(
            "buffer-chest",
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
        container1 = LogisticBufferContainer("buffer-chest")
        container2 = LogisticBufferContainer(
            "buffer-chest",
            bar=10,
            request_filters={"sections": [{"index":1, "filters": [{"name": "utility-science-pack", "index": 1, "count": 10}]}]},
            tags={"some": "stuff"},
        )
        container2.validate().reissue_all()

        container1.merge(container2)
        del container2

        assert container1.bar == 10
        assert container1.request_filters == RequestFiltersMixin.Format.RequestFilters(
            sections=[
                {
                    "index": 1,
                    "filters": [{"name": "utility-science-pack", "index": 1, "count": 10}]
                }
            ]
        )
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
