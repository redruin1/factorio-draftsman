# agricultural_tower.py

from draftsman.classes.entity import Entity
from draftsman.classes.mixins import (
    CircuitConditionMixin,
    CircuitEnableMixin,
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
class AgriculturalTower(
    LogisticConditionMixin,
    CircuitConditionMixin,
    CircuitEnableMixin,
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


draftsman_converters.add_hook_fns(
    AgriculturalTower,
    lambda fields: {("control_behavior", "read_contents"): fields.read_contents.name},
)
