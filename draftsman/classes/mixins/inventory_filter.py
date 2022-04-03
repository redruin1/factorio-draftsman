# inventory_filter.py
# -*- encoding: utf-8 -*-

from __future__ import unicode_literals

from draftsman import signatures
from draftsman.data import entities
from draftsman.data import signals
from draftsman.error import InvalidItemError, BarIndexError, FilterIndexError
from draftsman.warning import BarIndexWarning

from schema import SchemaError
import six
import warnings


class InventoryFilterMixin(object):
    """
    Allows inventories to set content filters. Used in cargo wagons.
    """

    def __init__(self, name, similar_entities, **kwargs):
        # type: (str, list[str], **dict) -> None
        super(InventoryFilterMixin, self).__init__(name, similar_entities, **kwargs)

        self._inventory_size = entities.raw[self.name]["inventory_size"]

        self.inventory = {}
        if "inventory" in kwargs:
            self.inventory = kwargs["inventory"]
            self.unused_args.pop("inventory")
        self._add_export("inventory", lambda x: len(x) != 0)

    # =========================================================================

    @property
    def inventory_size(self):
        # type: () -> int
        """
        Read Only
        TODO
        """
        return self._inventory_size

    # =========================================================================

    @property
    def inventory(self):
        # type: () -> dict
        """
        TODO
        """
        return self._inventory

    @inventory.setter
    def inventory(self, value):
        # type: (dict) -> None
        if value is None:
            self._inventory = {}
        else:
            try:
                self._inventory = signatures.INVENTORY_FILTER.validate(value)
            except SchemaError:
                # TODO: more verbose
                raise TypeError("Invalid inventory format")

    # =========================================================================

    @property
    def bar(self):
        # type: () -> int
        """
        TODO
        """
        return self._inventory.get("bar", None)

    @bar.setter
    def bar(self, value):
        # type: (int) -> None
        if value is None:
            self._inventory.pop("bar", None)
            return

        if not isinstance(value, int):
            raise TypeError("'bar' must be an int")

        if not 0 <= value < 65536:
            raise BarIndexError("Bar index ({}) not in range [0, 65536)".format(value))
        elif value >= self.inventory_size:
            warnings.warn(
                "Bar index ({}) not in range [0, {})".format(
                    value, self.inventory_size
                ),
                BarIndexWarning,
                stacklevel=2,
            )

        self._inventory["bar"] = value

    # =========================================================================

    def set_inventory_filter(self, index, item):
        # type: (int, str) -> None
        """
        Sets the item filter at location `index` to `name`. If `name` is set to
        `None` the item filter at that location is removed.

        `index`: [0-39] (0-indexed)
        """
        if "filters" not in self.inventory:
            self.inventory["filters"] = []

        try:
            index = signatures.INTEGER.validate(index)
        except SchemaError:
            # TODO: more verbose
            raise TypeError("Invalid index format")
        if item is not None:
            # Make sure item string is unicode
            item = six.text_type(item)
            if item not in signals.item:  # FIXME: maybe items.raw?
                raise InvalidItemError(item)

        if not 0 <= index < self.inventory_size:
            raise FilterIndexError(
                "Filter index ({}) not in range [0, {})".format(
                    index, self.inventory_size
                )
            )

        # Check to see if filters already contains an entry with the same index
        for i, filter in enumerate(self.inventory["filters"]):
            if filter["index"] == index + 1:  # Index already exists in the list
                if item is None:  # Delete the entry
                    del self.inventory["filters"][i]
                else:  # Set the new value
                    # self.inventory["filters"][i] = {"index": index+1,"name": item}
                    self.inventory["filters"][i]["name"] = item
                return

        # If no entry with the same index was found
        self.inventory["filters"].append({"index": index + 1, "name": item})

    def set_inventory_filters(self, filters):
        # type: (list) -> None
        """
        Sets the item filters for the inserter or loader.
        TODO: maybe swap this out for cargo_wagon.filters = filters?
        """
        if filters is None:
            self.inventory.pop("filters", None)
            return

        # Make sure filters conforms
        # TODO

        # Make sure the items are item signals
        for item in filters:
            if isinstance(item, dict):
                item = item["name"]
            if item not in signals.item:
                raise InvalidItemError(item)

        for i in range(len(filters)):
            if isinstance(filters[i], six.string_types):
                self.set_inventory_filter(i, filters[i])
            else:  # dict
                self.set_inventory_filter(i, filters[i]["name"])
