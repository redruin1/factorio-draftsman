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


_parent_hook = (
    draftsman_converters.get_version((2, 0))
    .get_converter()
    .get_structure_hook(LogisticRequestContainer)
)


def make_structure_hook(cls, converter: cattrs.Converter):
    # parent_hook = converter.get_structure_hook(LogisticRequestContainer)

    def structure_hook(d: dict, type: type):
        # print(d)
        if "request_filters" in d:
            # Populate with a single section
            filters = d["request_filters"]
            d["request_filters"] = {"sections": [{"index": 1, "filters": filters}]}
        # TODO: what about request_from_buffers?
        # print(d)
        return _parent_hook(d, type)

    return structure_hook


draftsman_converters.get_version((1, 0)).register_structure_hook_factory(
    lambda cls: issubclass(cls, LogisticRequestContainer), make_structure_hook
)

# TODO: unstructure hook
