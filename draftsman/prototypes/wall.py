# wall.py

from draftsman.classes.entity import Entity
from draftsman.classes.mixins import (
    CircuitConditionMixin,
    CircuitEnableMixin,
    ControlBehaviorMixin,
    CircuitConnectableMixin,
    DirectionalMixin,
)
from draftsman.serialization import draftsman_converters
from draftsman.signatures import SignalID
from draftsman.utils import fix_incorrect_pre_init
from draftsman.validators import instance_of

from draftsman.data.entities import walls

import attrs
from typing import Optional


@fix_incorrect_pre_init
@attrs.define
class Wall(
    CircuitConditionMixin,
    ControlBehaviorMixin,
    CircuitConnectableMixin,
    DirectionalMixin,
    Entity,
):
    """
    A static barrier that acts as protection for structures.
    """

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

    output_signal: Optional[SignalID] = attrs.field(
        factory=lambda: SignalID(name="signal-G", type="virtual"),
        converter=SignalID.converter,
        validator=instance_of(Optional[SignalID]),
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


draftsman_converters.get_version((1, 0)).add_hook_fns(
    Wall,
    lambda fields: {
        ("control_behavior", "circuit_open_gate"): fields.circuit_enabled.name,
        ("control_behavior", "circuit_read_sensor"): fields.read_gate.name,
        ("control_behavior", "output_signal"): fields.output_signal.name,
    },
)

draftsman_converters.get_version((2, 0)).add_hook_fns(
    Wall,
    lambda fields: {
        ("control_behavior", "circuit_open_gate"): fields.circuit_enabled.name,
        ("control_behavior", "circuit_read_gate"): fields.read_gate.name,
        ("control_behavior", "output_signal"): fields.output_signal.name,
    },
)
