# test_logistic_request_container.py

from draftsman.constants import LogisticModeOfOperation, ValidationMode
from draftsman.classes.mixins import RequestFiltersMixin
from draftsman.entity import (
    LogisticRequestContainer,
    logistic_request_containers,
    Container,
)
from draftsman.error import DataFormatError
from draftsman.signatures import SignalFilter, Section
from draftsman.warning import (
    UnknownEntityWarning,
    UnknownItemWarning,
    UnknownKeywordWarning,
)

from draftsman.data import mods

from collections.abc import Hashable
import pytest


class TestLogisticRequestContainer:
    def test_constructor_init(self):
        request_chest = LogisticRequestContainer(
            "requester-chest",
            tile_position=[15, 3],
            bar=5,
        )
        assert request_chest.to_dict() == {
            "name": "requester-chest",
            "position": {"x": 15.5, "y": 3.5},
            "bar": 5,
        }
        request_chest = LogisticRequestContainer(
            "requester-chest",
            position={"x": 15.5, "y": 1.5},
            bar=5,
            tags={"A": "B"},
        )
        assert request_chest.to_dict() == {
            "name": "requester-chest",
            "position": {"x": 15.5, "y": 1.5},
            "bar": 5,
            "tags": {"A": "B"},
        }

        request_chest = LogisticRequestContainer(
            request_filters={
                "sections": [{"index": 1, "filters": [("iron-ore", 100)]}],
                "request_from_buffers": True,
            }
        )
        assert request_chest.to_dict() == {
            "name": "requester-chest",
            "position": {"x": 0.5, "y": 0.5},
            "request_filters": {
                "sections": [
                    {
                        "index": 1,
                        "filters": [{"index": 1, "name": "iron-ore", "count": 100}],
                    }
                ],
                "request_from_buffers": True,
            },
        }

        request_chest = LogisticRequestContainer(
            request_filters=[{"index": 1, "name": "iron-ore", "count": 100}]
        )
        assert request_chest.to_dict() == {
            "name": "requester-chest",
            "position": {"x": 0.5, "y": 0.5},
            "request_filters": [{"index": 1, "name": "iron-ore", "count": 100}],
        }

        # Warnings
        with pytest.warns(UnknownKeywordWarning):
            LogisticRequestContainer(
                "requester-chest", position=[0, 0], invalid_keyword="100"
            ).validate().reissue_all()
        with pytest.warns(UnknownKeywordWarning):
            LogisticRequestContainer(
                control_behavior={"unused_key": "something"}
            ).validate().reissue_all()
        with pytest.warns(UnknownEntityWarning):
            LogisticRequestContainer(
                "this is not a logistics storage chest"
            ).validate().reissue_all()

        # Errors
        # Raises schema errors when any of the associated data is incorrect
        with pytest.raises(TypeError):
            LogisticRequestContainer("requester-chest", id=25).validate().reissue_all()
        with pytest.raises(TypeError):
            LogisticRequestContainer(
                "requester-chest", position=TypeError
            ).validate().reissue_all()
        with pytest.raises(DataFormatError):
            LogisticRequestContainer(
                "requester-chest", bar="not even trying"
            ).validate().reissue_all()
        with pytest.raises(DataFormatError):
            LogisticRequestContainer(
                "requester-chest",
                request_filters=["very", "wrong"],
            ).validate().reissue_all()
        with pytest.raises(DataFormatError):
            LogisticRequestContainer(
                control_behavior="incorrect"
            ).validate().reissue_all()

    def test_power_and_circuit_flags(self):
        for name in logistic_request_containers:
            container = LogisticRequestContainer(name)
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
            chest = LogisticRequestContainer("passive-provider-chest", quality=quality)
            assert chest.inventory_size == size

    def test_logistics_mode(self):
        container = LogisticRequestContainer("requester-chest")
        assert container.mode_of_operation == None
        assert container.to_dict() == {
            "name": "requester-chest",
            "position": {"x": 0.5, "y": 0.5},
        }

        # Set int
        container.mode_of_operation = 0
        assert container.mode_of_operation == LogisticModeOfOperation.SEND_CONTENTS
        assert container.to_dict() == {
            "name": "requester-chest",
            "position": {"x": 0.5, "y": 0.5},
            "control_behavior": {"circuit_mode_of_operation": 0},
        }

        # Set Enum
        container.mode_of_operation = LogisticModeOfOperation.SET_REQUESTS
        assert container.mode_of_operation == LogisticModeOfOperation.SET_REQUESTS
        assert container.to_dict() == {
            "name": "requester-chest",
            "position": {"x": 0.5, "y": 0.5},
            "control_behavior": {"circuit_mode_of_operation": 1},
        }

        # Set int outside range of enum
        with pytest.raises(DataFormatError):
            container.mode_of_operation = -1

        # Turn of validation
        container.validate_assignment = "none"
        assert container.validate_assignment == ValidationMode.NONE
        container.mode_of_operation = -1
        assert container.mode_of_operation == -1
        assert container.to_dict() == {
            "name": "requester-chest",
            "position": {"x": 0.5, "y": 0.5},
            "control_behavior": {"circuit_mode_of_operation": -1},
        }

    def test_set_requests(self):
        container = LogisticRequestContainer("requester-chest")

        # Shorthand
        section = container.add_section()
        section.filters = [
            ("iron-ore", 100),
            ("copper-ore", 200),
            ("coal", 300),
        ]
        assert container.sections[-1].filters == [
            SignalFilter(index=1, name="iron-ore", count=100),
            SignalFilter(index=2, name="copper-ore", count=200),
            SignalFilter(index=3, name="coal", count=300),
        ]

        # Longhand
        section.filters = [
            {"index": 1, "name": "iron-ore", "count": 100},
            {"index": 2, "name": "copper-ore", "count": 200},
            {"index": 3, "name": "coal", "count": 300},
        ]
        assert container.sections[-1].filters == [
            SignalFilter(index=1, name="iron-ore", count=100),
            SignalFilter(index=2, name="copper-ore", count=200),
            SignalFilter(index=3, name="coal", count=300),
        ]

    # def test_set_request_filter(self): # TODO: reimplement
    #     container = LogisticRequestContainer("requester-chest")

    #     container.set_request_filter(0, "iron-ore", 100)
    #     container.set_request_filter(1, "copper-ore", 200)
    #     assert container.request_filters == [
    #         RequestFilter(index=1, name="iron-ore", count=100),
    #         RequestFilter(index=2, name="copper-ore", count=200),
    #     ]

    #     # Replace existing
    #     container.set_request_filter(1, "wooden-chest", 123)
    #     assert container.request_filters == [
    #         RequestFilter(index=1, name="iron-ore", count=100),
    #         RequestFilter(index=2, name="wooden-chest", count=123),
    #     ]

    #     # Omitted count
    #     container.set_request_filter(0, "steel-chest")
    #     assert container.request_filters == [
    #         RequestFilter(index=1, name="steel-chest", count=None),
    #         RequestFilter(index=2, name="wooden-chest", count=123),
    #     ]

    #     # Delete existing
    #     container.set_request_filter(1, None)
    #     assert container.request_filters == [
    #         RequestFilter(index=1, name="steel-chest", count=None),
    #     ]

    #     # None case
    #     container.request_filters = None
    #     assert container.request_filters == None

    #     # Create from None
    #     container.set_request_filter(0, "copper-ore", 200)
    #     assert container.request_filters == [
    #         RequestFilter(index=1, name="copper-ore", count=200),
    #     ]

    #     with pytest.raises(DataFormatError):
    #         container.set_request_filter("incorrect", "incorrect")

    #     # Unknown item
    #     # No warning with minimum
    #     container.validate_assignment = "minimum"
    #     assert container.validate_assignment == ValidationMode.MINIMUM
    #     container.set_request_filter(0, "who-knows?", 100)
    #     assert container.request_filters == [
    #         RequestFilter(index=1, name="who-knows?", count=100),
    #     ]

    #     container.validate_assignment = ValidationMode.STRICT
    #     with pytest.warns(UnknownItemWarning):
    #         container.set_request_filter(0, "who-knows?", 100)

    # @pytest.mark.skipif(__factorio_version_info < (2,), "1.0")
    # def test_set_request_filters(self): # TODO: reimplement
    #     container = LogisticRequestContainer("requester-chest")

    #     # Shorthand
    #     container.set_request_filters(
    #         [("iron-ore", 100), ("copper-ore", 200), ("coal", 300)]
    #     )
    #     assert container.request_filters == [
    #         RequestFilter(index=1, name="iron-ore", count=100),
    #         RequestFilter(index=2, name="copper-ore", count=200),
    #         RequestFilter(index=3, name="coal", count=300),
    #     ]

    #     # Longhand
    #     container.set_request_filters(
    #         [
    #             {"index": 1, "name": "iron-ore", "count": 100},
    #             {"index": 2, "name": "copper-ore", "count": 200},
    #             {"index": 3, "name": "coal", "count": 300},
    #         ]
    #     )
    #     assert container.request_filters == [
    #         RequestFilter(index=1, name="iron-ore", count=100),
    #         RequestFilter(index=2, name="copper-ore", count=200),
    #         RequestFilter(index=3, name="coal", count=300),
    #     ]

    #     # Ensure error in all circumstances
    #     container.validate_assignment = "none"
    #     assert container.validate_assignment == ValidationMode.NONE
    #     with pytest.raises(DataFormatError):
    #         container.set_request_filters("incorrect")

    def test_request_from_buffers(self):
        container = LogisticRequestContainer("requester-chest")
        assert container.request_from_buffers == False
        assert container.to_dict() == {
            "name": "requester-chest",
            "position": {"x": 0.5, "y": 0.5},
        }

        container.request_from_buffers = True
        assert container.request_from_buffers == True
        assert container.to_dict() == {
            "name": "requester-chest",
            "position": {"x": 0.5, "y": 0.5},
            "request_filters": {"request_from_buffers": True},
        }

        with pytest.raises(DataFormatError):
            container.request_from_buffers = "incorrect"

        container.validate_assignment = "none"
        assert container.validate_assignment == ValidationMode.NONE

        container.request_from_buffers = "incorrect"
        assert container.request_from_buffers == "incorrect"
        assert container.to_dict() == {
            "name": "requester-chest",
            "position": {"x": 0.5, "y": 0.5},
            "request_filters": {"request_from_buffers": "incorrect"},
        }

    def test_mergable_with(self):
        container1 = LogisticRequestContainer("requester-chest")
        container2 = LogisticRequestContainer(
            "requester-chest",
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
        container1 = LogisticRequestContainer("requester-chest")
        container2 = LogisticRequestContainer(
            "requester-chest",
            bar=10,
            request_filters={
                "sections": [
                    {
                        "index": 1,
                        "filters": [
                            {"name": "utility-science-pack", "index": 1, "count": 10}
                        ],
                    }
                ]
            },
            tags={"some": "stuff"},
        )

        container1.merge(container2)
        del container2

        assert container1.bar == 10
        assert (
            container1.request_filters
            == LogisticRequestContainer.Format.LogisticsRequestFilters(
                sections=[
                    {
                        "index": 1,
                        "filters": [
                            {"name": "utility-science-pack", "index": 1, "count": 10}
                        ],
                    }
                ]
            )
        )
        assert container1.tags == {"some": "stuff"}

    def test_eq(self):
        container1 = LogisticRequestContainer("requester-chest")
        container2 = LogisticRequestContainer("requester-chest")

        assert container1 == container2

        container1.tags = {"some": "stuff"}

        assert container1 != container2

        container = Container()

        assert container1 != container
        assert container2 != container

        # hashable
        assert isinstance(container1, Hashable)
