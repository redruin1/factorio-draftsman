# test_logistic_active_container.py

from draftsman.constants import LogisticModeOfOperation, InventoryType
from draftsman.entity import (
    LogisticActiveContainer,
    logistic_active_containers,
    Container,
)
from draftsman.signatures import BlueprintInsertPlan
from draftsman.error import DataFormatError
from draftsman.warning import UnknownEntityWarning

from draftsman.data import mods

from collections.abc import Hashable
import pytest


@pytest.fixture
def valid_active_container():
    return LogisticActiveContainer(
        id="test",
        quality="uncommon",
        tile_position=(1, 1),
        read_contents=False,
        tags={"blah": "blah"},
    )


class TestActiveContainer:
    def test_constructor_init(self):
        active_chest = LogisticActiveContainer(
            tile_position={"x": 15, "y": 3},
            bar=5,
        )
        assert active_chest.to_dict(version=(2, 0)) == {
            "name": "active-provider-chest",
            "position": {"x": 15.5, "y": 3.5},
            "bar": 5,
        }

        active_chest = LogisticActiveContainer(
            position={"x": 15.5, "y": 1.5},
            bar=5,
            tags={"A": "B"},
        )
        assert active_chest.to_dict(version=(2, 0)) == {
            "name": "active-provider-chest",
            "position": {"x": 15.5, "y": 1.5},
            "bar": 5,
            "tags": {"A": "B"},
        }
        # Warnings
        with pytest.warns(UnknownEntityWarning):
            LogisticActiveContainer("this is not an active provider chest")

        # Errors
        # Raises schema errors when any of the associated data is incorrect
        with pytest.raises(TypeError):
            LogisticActiveContainer(id=25)

        with pytest.raises(DataFormatError):
            LogisticActiveContainer(position=TypeError)

        with pytest.raises(DataFormatError):
            LogisticActiveContainer(bar="not even trying")

    def test_from_dict(self):
        # TODO: test importing this string into 2.0 and see if Factorio is smart
        # and actually sends the modules to the correct spots
        """0eNp9UMtqwzAQ/Jc5SwE/2jj6lVKKrSzpgrQykhxqjP49knvpqbeZZeexe2BxG62RJcMcYBskwXwcSPyQ2bVZ3leCAWfyUJDZNzanRH5xLA/tZ/vNQnpAUWC50w9MVz4VSDJnpl+/k+xfsvmFYl3430lhDamKg7QG1VAPw+VNYYcZK6hBkSyfvciRzTEIW2052o1zVbeyqUnXGO6bzfys4dpX7Jq9GUsreJ5k/nxA4Ukxnan91I3XW3+dpun91vWlvAAUYWNo"""

        # Test old 1.0 items format gets properly modernized
        old_dict = {
            "name": "logistic-chest-active-provider",
            "position": {"x": 0.5, "y": 0.5},
            "items": {"iron-ore": 50},
        }
        container = LogisticActiveContainer.from_dict(old_dict, version=(1, 0))
        assert container.position.x == container.position.y == 0.5
        assert container.item_requests == [
            BlueprintInsertPlan(
                **{
                    "id": {"name": "iron-ore", "quality": "normal"},
                    "items": {
                        "in_inventory": [
                            {
                                "inventory": 1,
                                "stack": 0,
                                "count": 50,
                            }
                        ]
                    },
                }
            )
        ]

    def test_to_dict(self):
        container = LogisticActiveContainer()

        container.set_item_request(
            "iron-ore", 50, quality="normal", inventory=InventoryType.CHEST
        )

        # On 1.0, read_contents has no effect whatsoever
        assert container.read_contents is True
        assert container.to_dict(
            version=(1, 0), exclude_defaults=False, exclude_none=False
        ) == {
            "name": "logistic-chest-active-provider",
            "position": {"x": 0.5, "y": 0.5},
            # "bar": None, # Factorio doesn't like this null
            "items": {
                "iron-ore": 50,
            },
            "connections": {},
            "control_behavior": {
                "circuit_condition": {"comparator": "<", "constant": 0},
                "circuit_mode_of_operation": LogisticModeOfOperation.SEND_CONTENTS,
            },
            "tags": {},
        }
        container.read_contents = False
        assert container.read_contents is False
        assert container.to_dict(
            version=(1, 0), exclude_defaults=False, exclude_none=False
        ) == {
            "name": "logistic-chest-active-provider",
            "position": {"x": 0.5, "y": 0.5},
            # "bar": None,
            "items": {
                "iron-ore": 50,
            },
            "connections": {},
            "control_behavior": {
                "circuit_condition": {"comparator": "<", "constant": 0},
                "circuit_mode_of_operation": LogisticModeOfOperation.SEND_CONTENTS,
            },
            "tags": {},
        }

        # On 2.0, read_contents has an effect, but it is translated into
        # LogisticModeOfOperation enum
        container.read_contents = True
        assert container.to_dict(
            version=(2, 0), exclude_defaults=False, exclude_none=False
        ) == {
            "name": "active-provider-chest",
            "position": {"x": 0.5, "y": 0.5},
            "quality": "normal",
            "mirror": False,
            # "bar": None,
            "items": [
                {
                    "id": {"name": "iron-ore", "quality": "normal"},
                    "items": {
                        "in_inventory": [
                            {
                                "inventory": InventoryType.CHEST,
                                "stack": 0,
                                "count": 50,
                            }
                        ],
                        "grid_count": 0,
                    },
                }
            ],
            "control_behavior": {
                "circuit_condition": {"comparator": "<", "constant": 0},
                "circuit_mode_of_operation": LogisticModeOfOperation.SEND_CONTENTS,
            },
            "tags": {},
        }
        container.read_contents = False
        assert container.to_dict(
            version=(2, 0), exclude_defaults=False, exclude_none=False
        ) == {
            "name": "active-provider-chest",
            "position": {"x": 0.5, "y": 0.5},
            "quality": "normal",
            "mirror": False,
            # "bar": None,
            "items": [
                {
                    "id": {"name": "iron-ore", "quality": "normal"},
                    "items": {
                        "in_inventory": [
                            {
                                "inventory": InventoryType.CHEST,
                                "stack": 0,
                                "count": 50,
                            }
                        ],
                        "grid_count": 0,
                    },
                }
            ],
            "control_behavior": {
                "circuit_condition": {"comparator": "<", "constant": 0},
                "circuit_mode_of_operation": LogisticModeOfOperation.NONE,
            },
            "tags": {},
        }

    def test_power_and_circuit_flags(self):
        for container_name in logistic_active_containers:
            container = LogisticActiveContainer(container_name)
            assert container.power_connectable == False
            assert container.dual_power_connectable == False
            assert container.circuit_connectable == True
            assert container.dual_circuit_connectable == False

    def test_size(self):
        chest = LogisticActiveContainer()
        assert chest.size == 48

        with pytest.warns(UnknownEntityWarning):
            assert LogisticActiveContainer("unknown-chest").size is None

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
            chest = LogisticActiveContainer(quality=quality)
            assert chest.size == size

    def test_mergable_with(self):
        container1 = LogisticActiveContainer()
        container2 = LogisticActiveContainer(bar=10, tags={"some": "stuff"})

        assert container1.mergable_with(container1)

        assert container1.mergable_with(container2)
        assert container2.mergable_with(container1)

        container2.tile_position = (1, 1)
        assert not container1.mergable_with(container2)

    def test_merge(self):
        container1 = LogisticActiveContainer()
        container2 = LogisticActiveContainer(bar=10, tags={"some": "stuff"})

        container1.merge(container2)
        del container2

        assert container1.bar == 10
        assert container1.tags == {"some": "stuff"}

    def test_eq(self):
        container1 = LogisticActiveContainer()
        container2 = LogisticActiveContainer()

        assert container1 == container2

        container1.tags = {"some": "stuff"}

        assert container1 != container2

        container = Container()

        assert container1 != container
        assert container2 != container

        # hashable
        assert isinstance(container1, Hashable)
