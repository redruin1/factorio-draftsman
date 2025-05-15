# infinity_container.py

from draftsman.classes.entity import Entity
from draftsman.classes.mixins import ItemRequestMixin, InventoryMixin
from draftsman.classes.vector import Vector, PrimitiveVector
from draftsman.constants import ValidationMode
from draftsman.error import DataFormatError
from draftsman.serialization import draftsman_converters
from draftsman.signatures import AttrsInfinityFilter, uint16, uint32
from draftsman.validators import instance_of

from draftsman.data.entities import infinity_containers
from draftsman.data import items

import attrs
import copy
from pydantic import ConfigDict, Field, ValidationError
from typing import Any, Literal, Optional, Union


@attrs.define
class InfinityContainer(ItemRequestMixin, InventoryMixin, Entity):
    """
    An entity used to create an infinite amount of any item.
    """

    @property
    def similar_entities(self) -> list[str]:
        return infinity_containers

    # =========================================================================

    def _filters_converter(value):
        if isinstance(value, list):
            for i, elem in enumerate(value):
                value[i] = AttrsInfinityFilter.converter(elem)
            return value
        else:
            return value

    filters: list[AttrsInfinityFilter] = attrs.field(
        factory=list,
        converter=_filters_converter,
        validator=instance_of(list[AttrsInfinityFilter]),
    )
    """
    The list of items to infinitely create or remove from this 
    entity's inventory.
    """

    # =========================================================================

    remove_unfiltered_items: bool = attrs.field(
        default=False, validator=instance_of(bool)
    )
    """
    Whether or not to remove items that exceed the amounts specified in the
    ``InfinityContainer``'s filters.

    :exception DataFormatError: If set to anything other than a ``bool``.
    """

    # =========================================================================

    def set_infinity_filter(
        self,
        index: uint16,
        item: Optional[str],
        mode: Literal["at-least", "at-most", "exactly", None] = "at-least",
        count: Optional[uint32] = None,
    ):
        """
        Sets an infinity filter.

        :param index: The index of the filter to set.
        :param name: The name of the item to interact with.
        :param mode: The manner in which to set the filter. Can be one of
            ``"at-least"``, ``"at-most"``, or ``"exactly"``.
        :param count: The amount of the item to request. If set to ``None``, the
            amount set will default to the stack size of ``name``, if name can
            be deduced to a valid item. Otherwise ``count`` will default to 0.
        """

        index = int(index)
        if count is None:
            if item is None:
                count = 0
            else:  # default count to the item's stack size
                count = items.raw.get(item, {}).get("stack_size", 0)

        # Check to see if filters already contains an entry with the same index
        existing_index = False
        for i, filter_entry in enumerate(self.filters):
            if index + 1 == filter_entry.index:  # Index already exists in the list
                if item is None:  # Delete the entry
                    del self.filters[i]
                    return
                else:  # Set the new value
                    existing_index = i
                break

        new_filter = AttrsInfinityFilter(
            index=index + 1,
            name=item,
            count=count,
            mode=mode,
        )

        if existing_index is not False:
            self.filters[existing_index] = new_filter
        else:  # No entry with the same index was found
            self.filters.append(new_filter)

    def merge(self, other: "InfinityContainer"):
        super().merge(other)

        self.filters = copy.deepcopy(other.filters)
        self.remove_unfiltered_items = other.remove_unfiltered_items

    # =========================================================================

    __hash__ = Entity.__hash__


InfinityContainer.add_schema(
    {
        "$id": "urn:factorio:entity:infinity-container",
        "properties": {
            "infinity_settings": {
                "type": "object",
                "properties": {
                    "remove_unfiltered_items": {"type": "boolean", "default": "false"},
                    "filters": {
                        "type": "array",
                        "items": {"$ref": "urn:factorio:infinity-filter"},
                        "maxItems": 1000,  # TODO: currently I'm assuming
                    },
                },
            }
        },
    }
)

draftsman_converters.add_hook_fns(
    InfinityContainer,
    lambda fields: {
        ("infinity_settings", "filters"): fields.filters.name,
        (
            "infinity_settings",
            "remove_unfiltered_items",
        ): fields.remove_unfiltered_items.name,
    },
)
