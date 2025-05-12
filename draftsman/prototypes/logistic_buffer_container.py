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
import cattrs


@attrs.define
class LogisticBufferContainer(
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
    A logistics container that requests items on a secondary priority.
    """

    # class Format(
    #     InventoryMixin.Format,
    #     ItemRequestMixin.Format,
    #     LogisticModeOfOperationMixin.Format,
    #     CircuitConditionMixin.Format,
    #     ControlBehaviorMixin.Format,
    #     CircuitConnectableMixin.Format,
    #     RequestFiltersMixin.Format,
    #     Entity.Format,
    # ):
    #     class ControlBehavior(
    #         LogisticModeOfOperationMixin.ControlFormat,
    #         CircuitConditionMixin.ControlFormat,
    #         DraftsmanBaseModel,
    #     ):
    #         pass

    #     control_behavior: Optional[ControlBehavior] = ControlBehavior()

    #     model_config = ConfigDict(title="LogisticBufferContainer")

    # def __init__(
    #     self,
    #     name: Optional[str] = get_first(logistic_buffer_containers),
    #     position: Union[Vector, PrimitiveVector] = None,
    #     tile_position: Union[Vector, PrimitiveVector] = (0, 0),
    #     bar: uint16 = None,
    #     request_filters: Optional[RequestFiltersMixin.Format.RequestFilters] = {},
    #     items: Optional[list[ItemRequest]] = [],
    #     control_behavior: Format.ControlBehavior = {},
    #     tags: dict[str, Any] = {},
    #     validate_assignment: Union[
    #         ValidationMode, Literal["none", "minimum", "strict", "pedantic"]
    #     ] = ValidationMode.STRICT,
    #     **kwargs
    # ):
    #     """
    #     TODO
    #     """

    #     super(LogisticBufferContainer, self).__init__(
    #         name,
    #         logistic_buffer_containers,
    #         position=position,
    #         tile_position=tile_position,
    #         bar=bar,
    #         request_filters=request_filters,
    #         items=items,
    #         control_behavior=control_behavior,
    #         tags=tags,
    #         **kwargs
    #     )

    #     self.validate_assignment = validate_assignment

    # =========================================================================

    @property
    def similar_entities(self) -> list[str]:
        return logistic_buffer_containers

    # =========================================================================

    __hash__ = Entity.__hash__


_parent_hook = (
    draftsman_converters.get_version((2, 0))
    .get_converter()
    .get_structure_hook(LogisticBufferContainer)
)


def make_structure_hook(cls, converter: cattrs.Converter):
    def structure_hook(d: dict, type: type):
        if "request_filters" in d:
            # Populate with a single section
            filters = d["request_filters"]
            d["request_filters"] = {"sections": [{"index": 1, "filters": filters}]}
        # TODO: what about request_from_buffers?
        return _parent_hook(d, type)

    return structure_hook


draftsman_converters.get_version((1, 0)).register_structure_hook_factory(
    lambda cls: issubclass(cls, LogisticBufferContainer), make_structure_hook
)

# TODO: unstructure hook
