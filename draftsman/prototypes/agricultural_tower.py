# agricultural_tower.py

from draftsman.classes.entity import Entity
from draftsman.classes.mixins import (
    CircuitConditionMixin,
    LogisticConditionMixin,
    ControlBehaviorMixin,
    CircuitConnectableMixin,
    EnergySourceMixin,
)
from draftsman.serialization import draftsman_converters
from draftsman.validators import instance_of

from draftsman.data.entities import agricultural_towers

import attrs


@attrs.define
class AgriculturalTower(  # TODO: this can probably request items
    LogisticConditionMixin,
    CircuitConditionMixin,
    ControlBehaviorMixin,
    CircuitConnectableMixin,
    EnergySourceMixin,
    Entity,
):
    """
    An entity that can plant and harvest growables.
    """

    @property
    def similar_entities(self) -> list[str]:
        return agricultural_towers

    # =========================================================================

    read_contents: bool = attrs.field(default=False, validator=instance_of(bool))
    """
    Whether or not to broadcast the entities inside of this tower's inventory to
    any connected circuit network.
    """

    # =========================================================================

    __hash__ = Entity.__hash__


AgriculturalTower.add_schema(None, version=(1, 0))

AgriculturalTower.add_schema(
    {
        "$id": "urn:factorio:entity:agricultural-tower",
        "type": "object",
        "properties": {
            "control_behavior": {
                "type": "object",
                "properties": {
                    "read_contents": {"type": "boolean", "default": "false"}
                },
            }
        },
    },
    version=(2, 0),
)


draftsman_converters.add_hook_fns(
    AgriculturalTower,
    lambda fields: {("control_behavior", "read_contents"): fields.read_contents.name},
)
