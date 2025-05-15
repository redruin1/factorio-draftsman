# wall.py

from draftsman.classes.entity import Entity
from draftsman.classes.mixins import (
    CircuitConditionMixin,
    CircuitEnableMixin,
    ControlBehaviorMixin,
    CircuitConnectableMixin,
)
from draftsman.serialization import draftsman_converters
from draftsman.signatures import AttrsSignalID
from draftsman.validators import instance_of

from draftsman.data.entities import walls

import attrs
from typing import Optional


@attrs.define
class Wall(
    CircuitConditionMixin,
    ControlBehaviorMixin,
    CircuitConnectableMixin,
    Entity,
):
    """
    A static barrier that acts as protection for structures.
    """

    # @schema(version=(1, 0))
    # def json_schema(self) -> dict:
    #     return {
    #         "$id": "factorio:wall"
    #     }

    # @schema(version=(2, 0))
    # def json_schema(self) -> dict:
    #     return {
    #         "$id": "factorio:wall"
    #     }

    # =========================================================================

    @property
    def similar_entities(self) -> list[str]:
        return walls

    # =========================================================================

    circuit_enabled: bool = attrs.field(default=True, validator=instance_of(bool))
    """
    Whether or not this gate should be activated based on a circuit condition. 
    """

    # =========================================================================

    read_gate: bool = attrs.field(default=False, validator=instance_of(bool))
    """
    Whether or not this entity should continuously output a unit signal whenever 
    the gate is open, with the type of this signal determined by 
    :py:attr:`.output_signal`.
    """

    # =========================================================================

    output_signal: Optional[AttrsSignalID] = attrs.field(
        factory=lambda: AttrsSignalID(name="signal-G", type="virtual"),
        converter=AttrsSignalID.converter,
        validator=instance_of(Optional[AttrsSignalID]),
        metadata={"never_null": True},
    )

    # =========================================================================

    def merge(self, other: "Wall"):
        super().merge(other)

        self.circuit_enabled = other.circuit_enabled
        self.read_gate = other.read_gate
        self.output_signal = other.output_signal

    # =========================================================================

    __hash__ = Entity.__hash__


Wall.add_schema(
    {
        "$id": "urn:factorio:entity:wall",
        "properties": {
            "control_behavior": {
                "type": "object",
                "properties": {
                    "circuit_open_gate": {"type": "boolean", "default": "true"},
                    "circuit_read_sensor": {"type": "boolean", "default": "false"},
                    "output_signal": {"$ref": "urn:factorio:signal-id"},
                },
            }
        },
    },
    version=(1, 0),
)

draftsman_converters.get_version((1, 0)).add_hook_fns(
    Wall,
    lambda fields: {
        ("control_behavior", "circuit_open_gate"): fields.circuit_enabled.name,
        ("control_behavior", "circuit_read_sensor"): fields.read_gate.name,
        ("control_behavior", "output_signal"): fields.output_signal.name,
    },
)

Wall.add_schema(
    {
        "$id": "urn:factorio:entity:wall",
        "properties": {
            "control_behavior": {
                "type": "object",
                "properties": {
                    "circuit_open_gate": {"type": "boolean", "default": "true"},
                    "circuit_read_gate": {"type": "boolean", "default": "false"},
                    "output_signal": {"$ref": "urn:factorio:signal-id"},
                },
            }
        },
    },
    version=(2, 0),
)

draftsman_converters.get_version((2, 0)).add_hook_fns(
    Wall,
    lambda fields: {
        ("control_behavior", "circuit_open_gate"): fields.circuit_enabled.name,
        ("control_behavior", "circuit_read_gate"): fields.read_gate.name,
        ("control_behavior", "output_signal"): fields.output_signal.name,
    },
)
