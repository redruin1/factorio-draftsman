# test_space_platform_hub.py

from draftsman.prototypes.space_platform_hub import (
    SpacePlatformHub,
    space_platform_hubs,
)
from draftsman.warning import UnknownEntityWarning

import pytest


@pytest.fixture
def valid_space_platform_hub():
    if len(space_platform_hubs) == 0:
        return None
    return SpacePlatformHub(
        "space-platform-hub",
        trash_not_requested=True,
        request_from_buffers=False,
        read_contents=False,
        send_to_platform=False,
        read_moving_from=True,
        read_moving_to=True,
        read_speed=True,
        speed_signal="signal-A",
        read_damage_taken=True,
        damage_taken_signal="signal-B",
        request_missing_construction_materials=False,
    )


def test_constructor():
    hub = SpacePlatformHub(
        "space-platform-hub",
        read_contents=False,
        send_to_platform=False,
        read_moving_from=True,
        read_moving_to=True,
        read_speed=True,
        speed_signal="signal-A",
        read_damage_taken=True,
        damage_taken_signal="signal-B",
        request_missing_construction_materials=False,
    )
    assert hub.to_dict() == {
        "name": "space-platform-hub",
        "position": {"x": 4.0, "y": 4.0},
        "control_behavior": {
            "read_contents": False,
            "send_to_platform": False,
            "read_moving_from": True,
            "read_moving_to": True,
            "read_speed": True,
            "speed_signal": {"name": "signal-A", "type": "virtual"},
            "read_damage_taken": True,
            "damage_taken_signal": {"name": "signal-B", "type": "virtual"},
        },
        "request_missing_construction_materials": False,
    }

    with pytest.warns(UnknownEntityWarning):
        SpacePlatformHub("unknown space platform hub")


def test_flags():
    for hub_name in space_platform_hubs:
        hub = SpacePlatformHub(hub_name)
        assert hub.power_connectable == False
        assert hub.dual_power_connectable == False
        assert hub.circuit_connectable == True
        assert hub.dual_circuit_connectable == False
