# logistic_storage_container.py

from draftsman.classes.entity import Entity
from draftsman.classes.mixins import (
    RequestItemsMixin,
    LogisticModeOfOperationMixin,
    CircuitConditionMixin,
    ControlBehaviorMixin,
    CircuitConnectableMixin,
    RequestFiltersMixin,
    InventoryMixin,
)
from draftsman.classes.vector import Vector, PrimitiveVector
from draftsman.constants import ValidationMode
from draftsman.signatures import ItemRequest, RequestFilter, uint16
from draftsman.utils import get_first

from draftsman.data.entities import logistic_storage_containers

from typing import Any, Literal, Optional, Union
from pydantic import ConfigDict


class LogisticStorageContainer(
    InventoryMixin,
    RequestItemsMixin,
    LogisticModeOfOperationMixin,
    CircuitConditionMixin,
    ControlBehaviorMixin,
    CircuitConnectableMixin,
    RequestFiltersMixin,
    Entity,
):
    """
    A logistics container that stores items not currently being used in the
    logistic network.
    """

    class Format(
        InventoryMixin.Format,
        RequestItemsMixin.Format,
        LogisticModeOfOperationMixin.Format,
        CircuitConditionMixin.Format,
        ControlBehaviorMixin.Format,
        CircuitConnectableMixin.Format,
        RequestFiltersMixin.Format,
        Entity.Format,
    ):
        class ControlBehavior(
            LogisticModeOfOperationMixin.ControlFormat,
            CircuitConditionMixin.ControlFormat,
        ):
            pass

        control_behavior: Optional[ControlBehavior] = ControlBehavior()

        model_config = ConfigDict(title="LogisticStorageContainer")

    def __init__(
        self,
        name: Optional[str] = get_first(logistic_storage_containers),
        position: Union[Vector, PrimitiveVector] = None,
        tile_position: Union[Vector, PrimitiveVector] = (0, 0),
        bar: Optional[uint16] = None,
        request_filters: list[RequestFilter] = [],
        items: Optional[list[ItemRequest]] = [],
        control_behavior: Optional[Format.ControlBehavior] = {},
        tags: dict[str, Any] = {},
        validate_assignment: Union[
            ValidationMode, Literal["none", "minimum", "strict", "pedantic"]
        ] = ValidationMode.STRICT,
        **kwargs
    ):
        """
        TODO
        """

        super().__init__(
            name,
            logistic_storage_containers,
            position=position,
            tile_position=tile_position,
            bar=bar,
            request_filters=request_filters,
            items=items,
            control_behavior=control_behavior,
            tags=tags,
            **kwargs
        )

        self.validate_assignment = validate_assignment

    # =========================================================================

    __hash__ = Entity.__hash__
