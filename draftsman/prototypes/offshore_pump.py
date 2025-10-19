# offshore_pump.py

from draftsman.classes.entity import Entity
from draftsman.classes.mixins import (
    LogisticConditionMixin,
    CircuitConditionMixin,
    ControlBehaviorMixin,
    CircuitConnectableMixin,
    EnergySourceMixin,
    DirectionalMixin,
)

from draftsman.data.entities import offshore_pumps

import attrs


@attrs.define
class OffshorePump(
    LogisticConditionMixin,
    CircuitConditionMixin,
    ControlBehaviorMixin,
    CircuitConnectableMixin,
    EnergySourceMixin,
    DirectionalMixin,
    Entity,
):
    """
    An entity that pumps a fluid from the environment.
    """

    @property
    def similar_entities(self) -> list[str]:
        return offshore_pumps

    # =========================================================================

    __hash__ = Entity.__hash__
