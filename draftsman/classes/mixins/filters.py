# filters.py

from draftsman.classes.exportable import Exportable
from draftsman.data import entities
from draftsman.serialization import draftsman_converters
from draftsman.signatures import (
    AttrsItemFilter,
    ItemName,
    int64,
)
from draftsman.validators import instance_of

import attrs
from typing import Literal, Optional


@attrs.define(slots=False)
class FiltersMixin(Exportable):
    """
    Allows the entity to specify item filters.
    """

    @property
    def filter_count(self) -> Optional[int]:
        """
        The number of filter slots that this Entity has in total. Equivalent to
        the ``"filter_count"`` key in Factorio's ``data.raw``. Returns ``None``
        if this entity's name is not recognized by Draftsman. Not exported; read
        only.
        """
        return entities.raw.get(self.name, {"filter_count": None}).get(
            "filter_count", 0
        )

    # =========================================================================

    use_filters: bool = attrs.field(default=False, validator=instance_of(bool))
    """
    Whether or not this inserter should use filters at all. Overrided by
    ``circuit_set_filters``, if present.
    """

    # =========================================================================

    def _filters_converter(value):
        if isinstance(value, list):
            for i, elem in enumerate(value):
                value[i] = AttrsItemFilter.converter(elem)
            return value
        else:
            return value

    filters: list[AttrsItemFilter] = attrs.field(
        factory=list,
        converter=_filters_converter,
        validator=instance_of(list[AttrsItemFilter]),
    )
    """
    The manually-set item filters that this inserter/loader will abide by. These
    values are overridden by filters set by the circuit network, if so 
    configured.
    """

    # =========================================================================

    def set_item_filter(
        self,
        index: int64,
        item: ItemName,
        quality: Literal[
            "normal", "uncommon", "rare", "epic", "legendary", "any"
        ] = "normal",
        comparator: Literal[">", "<", "=", "==", "≥", ">=", "≤", "<=", "≠", "!="] = "=",
    ):
        """
        Sets one of the item filters of the Entity. `index` in this function is
        in 0-based notation.

        :param index: The index of the filter to set.
        :param item: The string name of the item to filter.

        :exception IndexError: If ``index`` is set to a value exceeding or equal
            to ``filter_count``.
        :exception InvalidItemError: If ``item`` is not a valid item name.
        """
        if item is not None:
            new_entry = AttrsItemFilter(
                index=index, name=item, quality=quality, comparator=comparator
            )

        found_index = None
        for i in range(len(self.filters)):
            filter = self.filters[i]
            if filter.index == index + 1:
                if item is None:
                    del self.filters[i]
                else:
                    filter.name = item
                    filter.quality = quality
                    filter.comparator = comparator
                found_index = i
                break

        if found_index is None:
            # TODO: bisect
            self.filters.append(new_entry)

    # =========================================================================

    def merge(self, other: "FiltersMixin"):
        super().merge(other)

        self.filters = other.filters


FiltersMixin.add_schema(
    {
        "properties": {
            "use_filters": {"type": "boolean", "default": False},
            "filters": {"type": "array", "items": {"$ref": "urn:factorio:item-filter"}},
        }
    }
)


draftsman_converters.add_hook_fns(
    # {"$id": "factorio:item_filters_mixin"},
    FiltersMixin,
    lambda fields: {
        "use_filters": fields.use_filters.name,
        "filters": fields.filters.name,
    },
    lambda fields, converter: {
        "use_filters": fields.use_filters.name,
        "filters": (
            fields.filters,
            lambda inst: [converter.unstructure(e) for e in inst.filters],
        ),
    },
)
