# test_display_panel.py

from draftsman.constants import Direction
from draftsman.prototypes.display_panel import (
    DisplayPanel,
    display_panels,
)
from draftsman.warning import UnknownEntityWarning

import pytest


@pytest.fixture
def valid_display_panel():
    if len(display_panels) == 0:
        return None
    return DisplayPanel(
        "display-panel",
        id="test",
        quality="uncommon",
        tile_position=(2, 2),
        direction=Direction.EAST,
        text="test",
        icon="signal-A",
        always_show_in_alt_mode=True,
        show_in_chart=True,
        messages=[DisplayPanel.Message(icon="signal-B", text="test2")],
        tags={"blah": "blah"},
    )


def test_constructor():
    curved_rail = DisplayPanel("display-panel")

    with pytest.warns(UnknownEntityWarning):
        DisplayPanel("unknown display panel")


def test_json_schema():
    assert DisplayPanel.json_schema(version=(1, 0)) is None
    assert DisplayPanel.json_schema(version=(2, 0)) == {
        "$id": "urn:factorio:entity:display-panel",
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "type": "object",
        "properties": {
            "entity_number": {"$ref": "urn:uint64"},
            "name": {"type": "string"},
            "position": {"$ref": "urn:factorio:position"},
            "quality": {"$ref": "urn:factorio:quality-name"},
            "direction": {"enum": list(range(16)), "default": 0},
            "text": {"type": "string"},
            "icon": {"oneOf": [{"$ref": "urn:factorio:signal-id"}, {"type": "null"}]},
            "always_show": {"type": "boolean", "default": "false"},
            "show_in_chart": {"type": "boolean", "default": "false"},
            "control_behavior": {
                "type": "object",
                "properties": {
                    "parameters": {
                        "type": "array",
                        "items": {"$ref": "urn:factorio:entity:display-panel:message"},
                    }
                },
                "description": "Entity-specific structure which holds keys related to configuring how this entity acts.",
            },
            "tags": {"type": "object"},
        },
        "required": ["entity_number", "name", "position"],
    }


def test_flags():
    for panel_name in display_panels:
        panel = DisplayPanel(panel_name)
        assert panel.power_connectable == False
        assert panel.dual_power_connectable == False
        assert panel.circuit_connectable == True
        assert panel.dual_circuit_connectable == False
