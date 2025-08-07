# filters.py

from draftsman.classes.exportable import Exportable
from draftsman.data import entities
from draftsman.serialization import draftsman_converters
from draftsman.signatures import (
    Comparator,
    ItemFilter,
    ItemIDName,
    int64,
)
from draftsman.validators import instance_of

import attrs
import bisect
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
        if this entity's name is not recognized by Draftsman.
        """
        return entities.raw.get(self.name, {"filter_count": None}).get(
            "filter_count", 0
        )

    # =========================================================================

    use_filters: bool = attrs.field(default=False, validator=instance_of(bool))
    """
    .. serialized::

        This attribute is imported/exported from blueprint strings.

    Whether or not this inserter should use filters at all. Overrided by
    :py:attr:`~.CircuitSetFiltersMixin.circuit_set_filters`, if present.
    """

    # =========================================================================

    def _filters_converter(value):
        if isinstance(value, list):
            for i, elem in enumerate(value):
                value[i] = ItemFilter.converter(elem)
            return value
        else:
            return value

    filters: list[ItemFilter] = attrs.field(
        factory=list,
        converter=_filters_converter,
        validator=instance_of(list[ItemFilter]),
    )
    """
    .. serialized::

        This attribute is imported/exported from blueprint strings.

    The manually-set item filters that this inserter/loader will abide by. These
    values are overridden by filters set by the circuit network, if so 
    configured.
    """

    # =========================================================================

    def set_item_filter(
        self,
        index: int64,
        item: ItemIDName,
        quality: Literal[
            "normal", "uncommon", "rare", "epic", "legendary", "any"
        ] = "normal",
        comparator: Comparator = "=",
    ):
        """
        Sets one of the item filters of the Entity.

        :param index: The index of the filter to set. Should be less than
            :py:attr:`.filter_count`.
        :param item: The string name of the item to filter.
        :param quality: The item's quality.
        :param comparator: In what manner should the quality of the filter be
            interpreted - defaults to an exact match (``"="``), but can also be
            specified as a range.
        """
        if item is not None:
            new_entry = ItemFilter(
                index=index, name=item, quality=quality, comparator=comparator
            )

        found_index = None
        for i in range(len(self.filters)):
            filter = self.filters[i]
            if filter.index == index:
                if item is None:
                    del self.filters[i]
                else:
                    filter.name = item
                    filter.quality = quality
                    filter.comparator = comparator
                found_index = i
                break

        if found_index is None:
            bisect.insort(self.filters, new_entry, key=lambda e: e.index)

    # =========================================================================

    def merge(self, other: "FiltersMixin"):
        super().merge(other)

        self.filters = other.filters


draftsman_converters.add_hook_fns(
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
