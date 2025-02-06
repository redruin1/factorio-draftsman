# logistic_request_container.py

from draftsman.classes.entity import Entity
from draftsman.classes.exportable import attempt_and_reissue
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
from draftsman.signatures import (
    DraftsmanBaseModel,
    ItemRequest,
    uint16,
)
from draftsman.utils import get_first

from draftsman.data.entities import logistic_request_containers

from pydantic import ConfigDict, Field
from typing import Any, Literal, Optional, Union


class LogisticRequestContainer(
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
    A logistics container that requests items with a primary priority.
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
            DraftsmanBaseModel,
        ):
            circuit_condition_enabled: Optional[bool] = Field(
                False, description="""Whether the condition is enabled."""
            )

        control_behavior: Optional[ControlBehavior] = ControlBehavior()

        class LogisticsRequestFilters(RequestFiltersMixin.Format.RequestFilters):
            request_from_buffers: Optional[bool] = Field(
                False,  # Different default
                description="""
                Whether or not this requester chest will pull from buffer chests.
                """,
            )

        request_filters: Optional[LogisticsRequestFilters] = LogisticsRequestFilters()

        model_config = ConfigDict(title="LogisticRequestContainer")

    def __init__(
        self,
        name: Optional[str] = get_first(logistic_request_containers),
        position: Union[Vector, PrimitiveVector] = None,
        tile_position: Union[Vector, PrimitiveVector] = (0, 0),
        bar: uint16 = None,
        request_filters: Optional[RequestFiltersMixin.Format.RequestFilters] = {},
        items: Optional[list[ItemRequest]] = [],
        control_behavior: Format.ControlBehavior = {},
        tags: dict[str, Any] = {},
        validate_assignment: Union[
            ValidationMode, Literal["none", "minimum", "strict", "pedantic"]
        ] = ValidationMode.STRICT,
        **kwargs
    ):
        self._root: __class__.Format

        super().__init__(
            name,
            logistic_request_containers,
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

    # def __eq__(self, other: "LogisticRequestContainer") -> bool:
    #     return (
    #         super().__eq__(other)
    #         and self.request_from_buffers == other.request_from_buffers
    #     )
