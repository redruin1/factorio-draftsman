# logistic_buffer_container.py

from draftsman.classes.entity import Entity
from draftsman.classes.mixins import (
    ItemRequestMixin,
    LogisticModeOfOperationMixin,
    CircuitConditionMixin,
    ControlBehaviorMixin,
    CircuitConnectableMixin,
    RequestFiltersMixin,
    InventoryMixin,
)
from draftsman.serialization import draftsman_converters

from draftsman.data.entities import logistic_buffer_containers

import attrs


@attrs.define
class LogisticBufferContainer(
    InventoryMixin,
    ItemRequestMixin,
    LogisticModeOfOperationMixin,
    # CircuitConditionMixin, # TODO: is this present on 2.0?
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


LogisticBufferContainer.add_schema(
    {
        "$id": "urn:factorio:entity:logistic-buffer-container",
    },
)
