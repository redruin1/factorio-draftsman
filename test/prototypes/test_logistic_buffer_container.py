# test_logistic_buffer_container.py

from draftsman.constants import LogisticModeOfOperation
from draftsman.entity import (
    LogisticBufferContainer,
    logistic_buffer_containers,
    Container,
)
from draftsman.error import DataFormatError
from draftsman.classes.mixins import RequestFiltersMixin
from draftsman.signatures import ManualSection, SignalFilter
from draftsman.warning import UnknownEntityWarning, UnknownKeywordWarning

from draftsman.data import mods

from collections.abc import Hashable
import pytest


@pytest.fixture
def valid_buffer_container():
    if len(logistic_buffer_containers) == 0:
        return None
    return LogisticBufferContainer(
        "buffer-chest",
        id="test",
        quality="uncommon",
        tile_position=(1, 1),
        mode_of_operation=LogisticModeOfOperation.SET_REQUESTS,
        trash_not_requested=True,
        sections=[
            ManualSection(
                index=1, filters=[SignalFilter(index=1, name="iron-ore", count=50)]
            )
        ],
        request_from_buffers=False,
        bar=10,
        tags={"blah": "blah"},
    )


class TestBufferContainer:
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

        # Warnings
        with pytest.warns(UnknownEntityWarning):
            LogisticBufferContainer(
                "this is not a buffer chest"
            ).validate().reissue_all()

        # Errors
        # Raises schema errors when any of the associated data is incorrect
        with pytest.raises(TypeError):
            LogisticBufferContainer("buffer-chest", id=25).validate().reissue_all()
        with pytest.raises(DataFormatError):
            LogisticBufferContainer(
                "buffer-chest", position=TypeError
            ).validate().reissue_all()
        with pytest.raises(DataFormatError):
            LogisticBufferContainer(
                "buffer-chest", bar="not even trying"
            ).validate().reissue_all()
        with pytest.raises(DataFormatError):
            LogisticBufferContainer(
                "buffer-chest", sections=["very", "wrong"]
            ).validate().reissue_all()
        with pytest.raises(DataFormatError):
            LogisticBufferContainer(
                "buffer-chest", tags="incorrect"
            ).validate().reissue_all()

    def test_power_and_circuit_flags(self):
        for name in logistic_buffer_containers:
            container = LogisticBufferContainer(name)
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
            chest = LogisticBufferContainer("buffer-chest", quality=quality)
            assert chest.size == size

    def test_mergable_with(self):
        container1 = LogisticBufferContainer("buffer-chest")
        container2 = LogisticBufferContainer(
            "buffer-chest",
            bar=10,
            sections=[
                {
                    "index": 1,
                    "filters": [
                        {"name": "utility-science-pack", "index": 1, "count": 10}
                    ],
                }
            ],
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
            sections=[
                {
                    "index": 1,
                    "filters": [
                        {
                            "name": "utility-science-pack",
                            "index": 1,
                            "count": 10,
                            "comparator": "=",
                        }
                    ],
                }
            ],
            tags={"some": "stuff"},
        )
        container2.validate().reissue_all()

        container1.merge(container2)
        del container2

        assert container1.bar == 10
        assert container1.sections == [
            ManualSection(
                **{
                    "index": 1,
                    "filters": [
                        {
                            "name": "utility-science-pack",
                            "index": 1,
                            "count": 10,
                            "comparator": "=",
                        }
                    ],
                }
            )
        ]
        assert container1.tags == {"some": "stuff"}

    def test_eq(self):
        container1 = LogisticBufferContainer("buffer-chest")
        container2 = LogisticBufferContainer("buffer-chest")

        assert container1 == container2

        container1.tags = {"some": "stuff"}

        assert container1 != container2

        container = Container()

        assert container1 != container
        assert container2 != container

        # hashable
        assert isinstance(container1, Hashable)

    def test_old_format_conversion(self):
        old_dict = {"name": "buffer-chest", "position": {"x": 0.5, "y": 0.5}}
        chest = LogisticBufferContainer.from_dict(old_dict, version=(1, 0))
        assert chest.to_dict(version=(1, 0)) == old_dict

        old_dict_with_filters = {  # TODO: actually validate this
            "name": "buffer-chest",
            "position": {"x": 0.5, "y": 0.5},
            "request_filters": [
                {
                    "index": 1,
                    "name": "iron-plate",
                    "count": 50,
                }
            ],
        }
        chest = LogisticBufferContainer.from_dict(old_dict_with_filters, version=(1, 0))
        assert len(chest.sections) == 1
        assert chest.sections == [
            ManualSection(
                index=1,
                filters=[
                    SignalFilter(
                        index=1,
                        name="iron-plate",
                        count=50,
                    )
                ],
            )
        ]

        # TODO: unstructure hook
