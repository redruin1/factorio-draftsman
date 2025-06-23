# logistic_buffer_container.py

from draftsman.classes.entity import Entity
from draftsman.classes.mixins import (
    LogisticModeOfOperationMixin,
    CircuitConditionMixin,
    CircuitEnableMixin,
    ControlBehaviorMixin,
    CircuitConnectableMixin,
    RequestFiltersMixin,
    InventoryMixin,
)

from draftsman.data.entities import logistic_buffer_containers

import attrs


@attrs.define
class LogisticBufferContainer(
    InventoryMixin,
    LogisticModeOfOperationMixin,
    CircuitConditionMixin,
    CircuitEnableMixin,
    ControlBehaviorMixin,
    CircuitConnectableMixin,
    RequestFiltersMixin,
    Entity,
):
    """
    A logistics container that requests items on a secondary priority.
    """

    @property
    def similar_entities(self) -> list[str]:
        return logistic_buffer_containers

    # =========================================================================

    __hash__ = Entity.__hash__
