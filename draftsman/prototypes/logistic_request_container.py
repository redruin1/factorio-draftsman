# logistic_request_container.py

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
from draftsman.validators import instance_of

from draftsman.data.entities import logistic_request_containers

import attrs
import cattrs


@attrs.define
class LogisticRequestContainer(
    InventoryMixin,
    ItemRequestMixin,
    LogisticModeOfOperationMixin,
    CircuitConditionMixin,
    ControlBehaviorMixin,
    CircuitConnectableMixin,
    RequestFiltersMixin,
    Entity,
):
    """
    A logistics container that requests items with a primary priority.
    """

    @property
    def similar_entities(self) -> list[str]:
        return logistic_request_containers

    # =========================================================================

    # TODO: should be evolve
    request_from_buffers: bool = attrs.field(
        default=False,
        validator=instance_of(bool),
    )

    # =========================================================================

    __hash__ = Entity.__hash__

