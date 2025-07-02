# infinity_container.py

from draftsman.classes.entity import Entity
from draftsman.classes.exportable import Exportable
from draftsman.classes.mixins import InventoryMixin
from draftsman.serialization import draftsman_converters
from draftsman.signatures import ItemIDName, QualityID, uint16, uint32
from draftsman.validators import instance_of, one_of

from draftsman.data.entities import infinity_containers
from draftsman.data import items

import attrs
import copy
from typing import Literal, Optional


@attrs.define
class InfinityContainer(InventoryMixin, Entity):
    """
    An entity used to create an infinite amount of any item.
    """

    @attrs.define
    class Filter(Exportable):
        index: uint16 = attrs.field(validator=instance_of(uint16))
        """
        Where in the infinity containers GUI this filter will exist,
        1-based.
        """
        name: ItemIDName = attrs.field(validator=instance_of(ItemIDName))
        """
        The name of the item to create/remove.
        """
        quality: QualityID = attrs.field(default="normal", validator=one_of(QualityID))
        """
        The quality of the item to create/remove.
        """
        count: uint32 = attrs.field(default=0, validator=instance_of(uint32))
        """
        The amount of this item to keep in the entity, as discerned
        by 'mode'.
        """
        mode: Literal["at-least", "at-most", "exactly"] = attrs.field(
            default="at-least", validator=one_of("at-least", "at-most", "exactly")
        )
        """
        What manner in which to create or remove this item from the 
        entity. 'at-least' sets 'count' as a lower-bound, 'at-most' 
        sets 'count' as an upper-bound, and exactly makes the 
        quantity of this item match 'count' exactly.
        """

    # =========================================================================

    @property
    def similar_entities(self) -> list[str]:
        return infinity_containers

    # =========================================================================

    filters: list[Filter] = attrs.field(
        factory=list,
        validator=instance_of(list[Filter]),
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

        new_filter = InfinityContainer.Filter(
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


draftsman_converters.get_version((1, 0)).add_hook_fns(
    InfinityContainer.Filter,
    lambda fields: {
        "index": fields.index.name,
        "name": fields.name.name,
        "count": fields.count.name,
        "mode": fields.mode.name,
    },
)

draftsman_converters.get_version((2, 0)).add_hook_fns(
    InfinityContainer.Filter,
    lambda fields: {
        "index": fields.index.name,
        "name": fields.name.name,
        "quality": fields.quality.name,
        "count": fields.count.name,
        "mode": fields.mode.name,
    },
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
