# filtered_inventory.py

from draftsman.classes.exportable import Exportable
from draftsman.data import entities
from draftsman.serialization import draftsman_converters
from draftsman.signatures import (
    AttrsItemFilter,
    ItemName,
    QualityName,
    Comparator,
    int64,
    uint16,
    ensure_bar_less_than_inventory_size,
)
from draftsman.validators import and_, instance_of

import attrs
from typing import Optional


@attrs.define(slots=False)
class FilteredInventoryMixin(Exportable):
    """
    Allows an Entity to set inventory filters.
    """

    @property
    def inventory_size(self) -> Optional[uint16]:
        """
        The number of inventory slots that this Entity has. Equivalent to the
        ``"inventory_size"`` key in Factorio's ``data.raw``. Returns ``None`` if
        this entity's name is not recognized by Draftsman. Not exported; read
        only.
        """
        return entities.raw.get(self.name, {"inventory_size": None})["inventory_size"]

    # =========================================================================

    def _inventory_filters_converter(value):
        if isinstance(value, list):
            for i, elem in enumerate(value):
                if isinstance(elem, str):
                    value[i] = AttrsItemFilter(index=i, name=elem)
                else:
                    value[i] = AttrsItemFilter.converter(elem)
        return value

    inventory_filters: list[AttrsItemFilter] = attrs.field(
        factory=list,
        converter=_inventory_filters_converter,
        validator=instance_of(list[AttrsItemFilter]),
    )
    """
    The list of filters applied to this entity's inventory slots.
    """

    # =========================================================================

    bar: Optional[uint16] = attrs.field(
        default=None,
        validator=and_(
            instance_of(Optional[uint16]), ensure_bar_less_than_inventory_size
        ),
    )
    """
    The limiting bar of the inventory. Used to prevent a the final-most
    slots in the inventory from accepting items.

    Raises :py:class:`~draftsman.warning.IndexWarning` if the set value
    exceeds the Entity's ``inventory_size`` attribute.

    :getter: Gets the bar location of the inventory, or ``None`` if not set.
    :setter: Sets the bar location of the inventory. Removes the entry from
        the ``inventory`` object.

    :exception TypeError: If set to anything other than an ``int`` or
        ``None``.
    :exception IndexError: If the set value lies outside of the range
        ``[0, 65536)``.
    """

    # =========================================================================

    def set_inventory_filter(
        self,
        index: int64,
        item: Optional[ItemName],
        quality: QualityName = "normal",
        comparator: Comparator = "=",
    ):
        """
        Sets the item filter at a particular index. If ``item`` is set to
        ``None``, the item filter at that location is removed.

        :param index: The index of the filter to set.
        :param item: The string name of the item to filter.

        :exception TypeError: If ``index`` is not an ``int`` or if ``item`` is
            neither a ``str`` nor ``None``.
        :exception InvalidItemError: If ``item`` is not a valid item name.
        :exception IndexError: If ``index`` lies outside the range
            ``[0, inventory_size)``.
        """
        if item is not None:
            new_entry = AttrsItemFilter(
                index=index, name=item, quality=quality, comparator=comparator
            )

        # new_filters = (
        #     self.inventory.filters if self.inventory.filters is not None else []
        # )

        # Check to see if filters already contains an entry with the same index
        found_index = None
        for i, filter in enumerate(self.inventory_filters):
            if filter.index == index + 1:  # Index already exists in the list
                if item is None:
                    # Delete the entry
                    del self.inventory_filters[i]
                else:
                    # Modify the existing value inplace
                    self.inventory_filters[i].name = item
                    self.inventory_filters[i].quality = quality
                    self.inventory_filters[i].comparator = comparator
                found_index = i
                break

        if found_index is None:
            # If no entry with the same index was found
            self.inventory_filters.append(new_entry)

    def merge(self, other: "FilteredInventoryMixin"):
        super().merge(other)

        self.inventory_filters = other.inventory_filters  # TODO: copy?
        self.bar = other.bar


FilteredInventoryMixin.add_schema(
    {
        "properties": {
            "inventory": {
                "type": "object",
                "properties": {
                    "filters": {
                        "type": "array",
                        "items": {"$ref": "urn:factorio:item-filter"},
                    },
                    "bar": {"oneOf": [{"type": "urn:uint16"}, {"type": "null"}]},
                },
            }
        }
    }
)

draftsman_converters.add_hook_fns(
    FilteredInventoryMixin,
    lambda fields: {
        ("inventory", "filters"): fields.inventory_filters.name,
        ("inventory", "bar"): fields.bar.name,
    },
)
