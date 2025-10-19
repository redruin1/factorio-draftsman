# transport_belt.py

from draftsman.classes.entity import Entity
from draftsman.classes.mixins import (
    CircuitReadContentsMixin,
    LogisticConditionMixin,
    CircuitConditionMixin,
    CircuitEnableMixin,
    ControlBehaviorMixin,
    CircuitConnectableMixin,
    DirectionalMixin,
)

from draftsman.data.entities import transport_belts

import attrs


@attrs.define
class TransportBelt(
    CircuitReadContentsMixin,
    LogisticConditionMixin,
    CircuitConditionMixin,
    CircuitEnableMixin,
    ControlBehaviorMixin,
    CircuitConnectableMixin,
    DirectionalMixin,
    Entity,
):
    """
    An entity that transports items.
    """

    @property
    def similar_entities(self) -> list[str]:
        return transport_belts

    # =========================================================================

    __hash__ = Entity.__hash__
