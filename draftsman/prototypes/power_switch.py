# power_switch.py

from draftsman.classes.entity import Entity
from draftsman.classes.mixins import (
    LogisticConditionMixin,
    CircuitConditionMixin,
    ControlBehaviorMixin,
    CircuitConnectableMixin,
    PowerConnectableMixin,
)
from draftsman.data import entities
from draftsman.serialization import draftsman_converters
from draftsman.validators import instance_of

from draftsman.data.entities import power_switches

import attrs


@attrs.define
class PowerSwitch(
    LogisticConditionMixin,
    CircuitConditionMixin,
    ControlBehaviorMixin,
    CircuitConnectableMixin,
    PowerConnectableMixin,
    Entity,
):
    """
    An entity that connects or disconnects a power network.
    """

    @property
    def similar_entities(self) -> list[str]:
        return power_switches

    # =========================================================================

    @property
    def dual_power_connectable(self) -> bool:
        return True

    # =========================================================================

    @property
    def maximum_wire_distance(self) -> float:
        # Power switches use a custom key (for some reason)
        return entities.raw.get(self.name, {"wire_max_distance": None}).get(
            "wire_max_distance", 0
        )

    # =========================================================================

    @property
    def circuit_wire_max_distance(self) -> float:
        # Power switches use a custom key (for some reason)
        return entities.raw.get(self.name, {"wire_max_distance": None}).get(
            "wire_max_distance", 0
        )

    # =========================================================================

    switch_state: bool = attrs.field(default=False, validator=instance_of(bool))
    """
    Whether the switch is passing electricity or not. This is a manual
    setting that is overridden by the circuit or logistic condition.

    :exception DataFormatError: If set to anything other than a ``bool``.
    """

    # =========================================================================

    def merge(self, other: "PowerSwitch") -> None:
        super().merge(other)

        self.switch_state = other.switch_state

    # =========================================================================

    __hash__ = Entity.__hash__


PowerSwitch.add_schema(
    {
        "$id": "urn:factorio:entity:power-switch",
        "properties": {"switch_state": {"type": "boolean", "default": "false"}},
    }
)

draftsman_converters.add_hook_fns(
    PowerSwitch,
    lambda fields: {"switch_state": fields.switch_state.name},
)
