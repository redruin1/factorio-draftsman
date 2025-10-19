# pump.py

from draftsman.classes.entity import Entity
from draftsman.classes.mixins import (
    LogisticConditionMixin,
    CircuitConditionMixin,
    ControlBehaviorMixin,
    CircuitConnectableMixin,
    EnergySourceMixin,
    DirectionalMixin,
)

from draftsman.data.entities import pumps

import attrs


@attrs.define
class Pump(
    LogisticConditionMixin,
    CircuitConditionMixin,
    ControlBehaviorMixin,
    CircuitConnectableMixin,
    EnergySourceMixin,
    DirectionalMixin,
    Entity,
):
    """
    An entity that aids fluid transfer through pipes.
    """

    @property
    def similar_entities(self) -> list[str]:
        return pumps

    # =========================================================================

    __hash__ = Entity.__hash__
