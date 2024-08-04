# logistic_request_container.py

from draftsman.classes.entity import Entity
from draftsman.classes.exportable import attempt_and_reissue
from draftsman.classes.mixins import (
    RequestItemsMixin,
    LogisticModeOfOperationMixin,
    ControlBehaviorMixin,
    CircuitConnectableMixin,
    RequestFiltersMixin,
    InventoryMixin,
)
from draftsman.classes.vector import Vector, PrimitiveVector
from draftsman.constants import ValidationMode
from draftsman.signatures import (
    Connections,
    DraftsmanBaseModel,
    RequestFilter,
    uint16,
    uint32,
)
from draftsman.utils import get_first

from draftsman.data.entities import logistic_request_containers

from pydantic import ConfigDict, Field
from typing import Any, Literal, Optional, Union


class LogisticRequestContainer(
    InventoryMixin,
    RequestItemsMixin,
    LogisticModeOfOperationMixin,
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
        ControlBehaviorMixin.Format,
        CircuitConnectableMixin.Format,
        RequestFiltersMixin.Format,
        Entity.Format,
    ):
        class ControlBehavior(
            LogisticModeOfOperationMixin.ControlFormat, DraftsmanBaseModel
        ):
            pass

        control_behavior: Optional[ControlBehavior] = ControlBehavior()

        request_from_buffers: Optional[bool] = Field(
            False,
            description="""
            Whether or not this requester chest will pull from buffer chests.
            """,
        )

        model_config = ConfigDict(title="LogisticRequestContainer")

    def __init__(
        self,
        name: Optional[str] = get_first(logistic_request_containers),
        position: Union[Vector, PrimitiveVector] = None,
        tile_position: Union[Vector, PrimitiveVector] = (0, 0),
        bar: uint16 = None,
        request_filters: list[RequestFilter] = [],
        items: dict[str, uint32] = {},  # TODO: ItemID
        connections: Connections = {},
        control_behavior: Format.ControlBehavior = {},
        request_from_buffers: bool = False,
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
            connections=connections,
            control_behavior=control_behavior,
            tags=tags,
            **kwargs
        )

        self.request_from_buffers = request_from_buffers

        self.validate_assignment = validate_assignment

    # =========================================================================

    @property
    def request_from_buffers(self) -> Optional[bool]:
        """
        Whether or not this requester can request from buffer chests.

        :getter: Gets whether or not to recieve from buffers.
        :setter: Sets whether or not to recieve from buffers.

        :exception TypeError: If set to anything other than a ``bool`` or ``None``.
        """
        return self._root.request_from_buffers

    @request_from_buffers.setter
    def request_from_buffers(self, value: Optional[bool]):
        if self.validate_assignment:
            result = attempt_and_reissue(
                self, type(self).Format, self._root, "request_from_buffers", value
            )
            self._root.request_from_buffers = result
        else:
            self._root.request_from_buffers = value

    # =========================================================================

    __hash__ = Entity.__hash__

    def __eq__(self, other) -> bool:
        return (
            super().__eq__(other)
            and self.request_from_buffers == other.request_from_buffers
        )
