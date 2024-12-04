# logistic_buffer_container.py

from draftsman.classes.entity import Entity
from draftsman.classes.mixins import (
    RequestItemsMixin,
    LogisticModeOfOperationMixin,
    ControlBehaviorMixin,
    CircuitConnectableMixin,
    RequestFiltersMixin,
    InventoryMixin,
)
from draftsman.classes.vector import Vector, PrimitiveVector
from draftsman.constants import LogisticModeOfOperation, ValidationMode
from draftsman.data.entities import of_type
from draftsman.error import DataFormatError
from draftsman.signatures import (
    Connections,
    DraftsmanBaseModel,
    RequestFilter,
    uint16,
    uint32,
)
from draftsman.utils import get_first

# from draftsman.data.entities import logistic_buffer_containers

from pydantic import ConfigDict
from typing import Any, Literal, Optional, Union


class LogisticBufferContainer(
    InventoryMixin,
    RequestItemsMixin,
    LogisticModeOfOperationMixin,
    ControlBehaviorMixin,
    CircuitConnectableMixin,
    RequestFiltersMixin,
    Entity,
):
    """
    A logistics container that requests items on a secondary priority.
    """

    class Format(
        InventoryMixin.Format,
        RequestItemsMixin.Format,
        LogisticModeOfOperationMixin.Format,
        ControlBehaviorMixin.Format,
        CircuitConnectableMixin.Format,
        RequestFiltersMixin.Format,
        Entity.Format,
    ):
        class ControlBehavior(LogisticModeOfOperationMixin.Format, DraftsmanBaseModel):
            pass

        control_behavior: Optional[ControlBehavior] = ControlBehavior()

        model_config = ConfigDict(title="LogisticBufferContainer")

    def __init__(
        self,
        name: Optional[str] = get_first(of_type["logistic-container"]),
        position: Union[Vector, PrimitiveVector] = None,
        tile_position: Union[Vector, PrimitiveVector] = (0, 0),
        bar: uint16 = None,
        request_filters: list[RequestFilter] = [],
        items: dict[str, uint32] = {},  # TODO: ItemID
        connections: Connections = {},
        control_behavior: Format.ControlBehavior = {},
        tags: dict[str, Any] = {},
        validate_assignment: Union[
            ValidationMode, Literal["none", "minimum", "strict", "pedantic"]
        ] = ValidationMode.STRICT,
        **kwargs
    ):
        """
        TODO
        """

        super(LogisticBufferContainer, self).__init__(
            name,
            of_type["logistic-container"],
            position=position,
            tile_position=tile_position,
            bar=bar,
            request_filters=request_filters,
            items=items,
            connections=connections,
            control_behavior=control_behavior,
            tags=tags,
            **kwargs
        )

        self.validate_assignment = validate_assignment

    # =========================================================================

    __hash__ = Entity.__hash__
