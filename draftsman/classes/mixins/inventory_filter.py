# inventory_filter.py
# -*- encoding: utf-8 -*-

from __future__ import unicode_literals

from draftsman import signatures
from draftsman.data import entities
from draftsman.data import items
from draftsman.error import (
    InvalidItemError,
    DataFormatError,
)
from draftsman.warning import IndexWarning

from schema import SchemaError
import six
import warnings


class InventoryFilterMixin(object):
    """
    Allows an Entity to set inventory filters. Only used on :py:class:`.CargoWagon`.
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
        The number of inventory slots that this Entity has. Equivalent to the
        ``"inventory_size"`` key in Factorio's ``data.raw``. Not exported; read
        only.

        :type: ``int``
        """
        return self._inventory_size

    # =========================================================================

    @property
    def inventory(self):
        # type: () -> dict
        """
        Inventory filter object. Contains the filter information under the
        ``"filters"`` key and the inventory limiting bar under the ``"bar"`` key.

        This attribute is in the following format::

            {
                "bar": int,
                "filters": [
                    {"index": int, "signal": {"name": str, "type": str}},
                    ...
                ]
            }

        :getter: Gets the value of the Entity's ``inventory`` object.
        :setter: Sets the value of the Entity's ``inventory`` object. Defaults
            to an empty ``dict`` if set to ``None``.
        :type: See :py:class:`draftsman.signatures.INVENTORY_FILTER`.

        :exception DataFormatError: If the set value differs from the
            ``INVENTORY_FILTER`` specification.
        """
        return self._inventory

    @inventory.setter
    def inventory(self, value):
        # type: (dict) -> None
        try:
            self._inventory = signatures.INVENTORY_FILTER.validate(value)
        except SchemaError as e:
            six.raise_from(DataFormatError(e), None)

    # =========================================================================

    @property
    def bar(self):
        # type: () -> int
        """
        The limiting bar of the inventory. Used to prevent a the final-most
        slots in the inventory from accepting items.

        Raises :py:class:`~draftsman.warning.IndexWarning` if the set value
        exceeds the Entity's ``inventory_size`` attribute.

        :getter: Gets the bar location of the inventory, or ``None`` if not set.
        :setter: Sets the bar location of the inventory. Removes the entry from
            the ``inventory`` object.
        :type: ``int``

        :exception TypeError: If set to anything other than an ``int`` or
            ``None``.
        :exception IndexError: If the set value lies outside of the range
            ``[0, 65536)``.
        """
        return self._inventory.get("bar", None)

    @bar.setter
    def bar(self, value):
        # type: (int) -> None
        if value is None:
            self._inventory.pop("bar", None)
            return

        if not isinstance(value, six.integer_types):
            raise TypeError("'bar' must be an int")

        if not 0 <= value < 65536:
            raise IndexError("Bar index ({}) not in range [0, 65536)".format(value))
        elif value >= self.inventory_size:
            warnings.warn(
                "Bar index ({}) not in range [0, {})".format(
                    value, self.inventory_size
                ),
                IndexWarning,
                stacklevel=2,
            )

        self._inventory["bar"] = value

    # =========================================================================

    def set_inventory_filter(self, index, item):
        # type: (int, str) -> None
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
        try:
            index = signatures.INTEGER.validate(index)
            item = signatures.STRING_OR_NONE.validate(item)
        except SchemaError as e:
            six.raise_from(TypeError(e), None)

        if "filters" not in self.inventory:
            self.inventory["filters"] = []

        if item is not None:
            # Make sure item string is unicode
            item = six.text_type(item)
            if item not in items.raw:
                raise InvalidItemError(item)

        if not 0 <= index < self.inventory_size:
            raise IndexError(
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
        Sets all the inventory filters of the Entity.

        ``filters`` can be either of the following formats::

            [{"index": int, "signal": {"name": item_name_1, "type": "item"}}, ...]
            # Or
            [{"index": int, "signal": item_name_1}, ...]
            # Or
            [item_name_1, item_name_2, ...]

        With the second format, the index of each item is set to it's position
        in the list. ``filters`` can also be ``None``, which will wipe all
        inventory filters that the Entity has.

        :param filters: The inventory filters to give the Entity.

        :exception DataFormatError: If the ``filters`` argument does not match
            the specification above.
        :exception InvalidItemError: If the item name of one of the entries is
            not valid.
        :exception IndexError: If the index of one of the entries lies outside
            the range ``[0, inventory_size)``.
        """
        if filters is None:
            self.inventory.pop("filters", None)
            return

        try:
            filters = signatures.FILTERS.validate(filters)
        except SchemaError as e:
            six.raise_from(DataFormatError(e), None)

        # Make sure the items are item signals
        for item in filters:
            if item["name"] not in items.raw:
                raise InvalidItemError(item)

        for i in range(len(filters)):
            self.set_inventory_filter(filters[i]["index"] - 1, filters[i]["name"])
