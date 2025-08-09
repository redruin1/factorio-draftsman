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
    return LogisticBufferContainer(
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
            tile_position=[15, 3],
            bar=5,
        )
        assert buffer_chest.to_dict(version=(2, 0)) == {
            "name": "buffer-chest",
            "position": {"x": 15.5, "y": 3.5},
            "bar": 5,
        }

        buffer_chest = LogisticBufferContainer(
            position={"x": 15.5, "y": 1.5},
            bar=5,
            tags={"A": "B"},
        )
        assert buffer_chest.to_dict(version=(2, 0)) == {
            "name": "buffer-chest",
            "position": {"x": 15.5, "y": 1.5},
            "bar": 5,
            "tags": {"A": "B"},
        }

        # Warnings
        with pytest.warns(UnknownEntityWarning):
            LogisticBufferContainer("this is not a buffer chest")

        # Errors
        # Raises schema errors when any of the associated data is incorrect
        with pytest.raises(TypeError):
            LogisticBufferContainer(id=25)
        with pytest.raises(DataFormatError):
            LogisticBufferContainer(position=TypeError)
        with pytest.raises(DataFormatError):
            LogisticBufferContainer(bar="not even trying")
        with pytest.raises(DataFormatError):
            LogisticBufferContainer(sections=["very", "wrong"])
        with pytest.raises(DataFormatError):
            LogisticBufferContainer(tags="incorrect")

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
            chest = LogisticBufferContainer(quality=quality)
            assert chest.size == size

    def test_mergable_with(self):
        container1 = LogisticBufferContainer()
        container2 = LogisticBufferContainer(
            bar=10,
            sections=[
                ManualSection(
                    index=1,
                    filters=[
                        SignalFilter(
                            index=1,
                            name="utility-science-pack",
                            count=10,
                        )
                    ],
                )
            ],
            tags={"some": "stuff"},
        )

        assert container1.mergable_with(container1)

        assert container1.mergable_with(container2)
        assert container2.mergable_with(container1)

        container2.tile_position = (1, 1)
        assert not container1.mergable_with(container2)

    def test_merge(self):
        container1 = LogisticBufferContainer()
        container2 = LogisticBufferContainer(
            bar=10,
            sections=[
                ManualSection(
                    index=1,
                    filters=[
                        SignalFilter(
                            index=1,
                            name="utility-science-pack",
                            count=10,
                        )
                    ],
                )
            ],
            tags={"some": "stuff"},
        )
        container2.validate().reissue_all()

        container1.merge(container2)
        del container2

        assert container1.bar == 10
        assert container1.sections == [
            ManualSection(
                index=1,
                filters=[
                    SignalFilter(
                        index=1,
                        name="utility-science-pack",
                        count=10,
                    )
                ],
            )
        ]
        assert container1.tags == {"some": "stuff"}

    def test_eq(self):
        container1 = LogisticBufferContainer()
        container2 = LogisticBufferContainer()

        assert container1 == container2

        container1.tags = {"some": "stuff"}

        assert container1 != container2

        container = Container()

        assert container1 != container
        assert container2 != container

        # hashable
        assert isinstance(container1, Hashable)

    def test_old_format_conversion(self):
        old_dict = {"name": "logistic-chest-buffer", "position": {"x": 0.5, "y": 0.5}}
        chest = LogisticBufferContainer.from_dict(old_dict, version=(1, 0))
        assert chest.to_dict(version=(1, 0)) == old_dict

        old_dict_with_filters = {  # TODO: actually validate this
            "name": "logistic-chest-buffer",
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
                index=0,
                filters=[
                    SignalFilter(
                        index=0,
                        name="iron-plate",
                        count=50,
                    )
                ],
            )
        ]

        # TODO: unstructure hook
