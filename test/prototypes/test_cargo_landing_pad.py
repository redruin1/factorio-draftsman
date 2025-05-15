# test_cargo_landing_pad.py

from draftsman.constants import LogisticModeOfOperation
from draftsman.prototypes.cargo_landing_pad import (
    CargoLandingPad,
    cargo_landing_pads,
)
from draftsman.signatures import ManualSection, SignalFilter
from draftsman.warning import UnknownEntityWarning

import pytest


@pytest.fixture
def valid_cargo_landing_pad():
    if len(cargo_landing_pads) == 0:
        return None
    return CargoLandingPad(
        "cargo-landing-pad",
        id="test",
        quality="uncommon",
        tile_position=(1, 1),
        mode_of_operation=LogisticModeOfOperation.NONE,
        trash_not_requested=True,
        request_from_buffers=False,  # TODO: this exists, but cannot be controlled via GUI...
        requests_enabled=False,  # TODO: this exists, but cannot be controlled via GUI...
        sections=[
            ManualSection(
                index=1, filters=[SignalFilter(index=0, name="iron-ore", count=100)]
            )
        ],
        tags={"blah": "blah"},
    )


def test_constructor():
    pad = CargoLandingPad(
        "cargo-landing-pad", mode_of_operation=LogisticModeOfOperation.SET_REQUESTS
    )
    assert pad.to_dict() == {
        "name": "cargo-landing-pad",
        "position": {"x": 4.0, "y": 4.0},
        "control_behavior": {
            "circuit_mode_of_operation": LogisticModeOfOperation.SET_REQUESTS,
        },
    }

    with pytest.warns(UnknownEntityWarning):
        CargoLandingPad("unknown landing pad")


def test_json_schema():
    assert CargoLandingPad.json_schema(version=(1, 0)) is None
    assert CargoLandingPad.json_schema(version=(2, 0)) == {
        "$id": "urn:factorio:entity:cargo-landing-pad",
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "type": "object",
        "properties": {
            "entity_number": {"$ref": "urn:uint64"},
            "name": {"type": "string"},
            "position": {"$ref": "urn:factorio:position"},
            "quality": {"$ref": "urn:factorio:quality-name"},
            "control_behavior": {
                "type": "object",
                "properties": {
                    "circuit_mode_of_operation": {"enum": [0, 1, 2], "default": 0},
                },
                "description": "Entity-specific structure which holds keys related to configuring how this entity acts.",
            },
            "request_filters": {
                "type": "object",
                "properties": {
                    "trash_not_requested": {"type": "boolean", "default": "false"},
                    "request_from_buffers": {"type": "boolean", "default": "true"},
                    "enabled": {"type": "boolean", "default": "true"},
                    "sections": {
                        "type": "array",
                        "items": {"$ref": "urn:factorio:manual-section"},
                        "maxItems": 100,
                    },
                },
            },
            "tags": {"type": "object"},
        },
        "required": ["entity_number", "name", "position"],
    }


def test_flags():
    for pad_name in cargo_landing_pads:
        pad = CargoLandingPad(pad_name)
        assert pad.power_connectable == False
        assert pad.dual_power_connectable == False
        assert pad.circuit_connectable == True
        assert pad.dual_circuit_connectable == False
