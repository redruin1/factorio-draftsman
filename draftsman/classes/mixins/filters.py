# filters.py
# -*- encoding: utf-8 -*-

from __future__ import unicode_literals

from draftsman.data import items, entities
from draftsman.error import InvalidItemError, DataFormatError
from draftsman import signatures

from schema import SchemaError
import six


class FiltersMixin(object):
    """
    Allows the entity to specify item filters.
    """

    def __init__(self, name, similar_entities, **kwargs):
        # type: (str, list[str], **dict) -> None
        super(FiltersMixin, self).__init__(name, similar_entities, **kwargs)

        self._filter_count = entities.raw[self.name].get("filter_count", 0)

        self.filters = None

        if "filters" in kwargs:
            self.set_item_filters(kwargs["filters"])
            self.unused_args.pop("filters")
        self._add_export("filters", lambda x: x is not None and len(x) != 0)

    # =========================================================================

    @property
    def filter_count(self):
        # type: () -> int
        """
        The number of filter slots that this Entity has in total. Equivalent to
        the ``"filter_count"`` key in Factorio's ``data.raw``. Not exported;
        read only.

        :type: ``int``
        """
        return self._filter_count

    # =========================================================================

    def set_item_filter(self, index, item):
        # type: (int, str) -> None
        """
        Sets one of the item filters of the Entity.

        :param index: The index of the filter to set.
        :param item: The string name of the item to filter.

        :exception IndexError: If ``index`` is set to a value exceeding or equal
            to ``filter_count``.
        :exception InvalidItemError: If ``item`` is not a valid item name.
        """
        if self.filters is None:
            self.filters = []

        # Check if index is ouside the range of the max filter slots
        if index >= self.filter_count:
            raise IndexError(
                "Index {} exceeds the maximum number of filter slots for this "
                "entity ({})".format(index, self.filter_count)
            )

        if item is not None:
            # Make sure item string is unicode
            item = six.text_type(item)
            if item not in items.raw:
                raise InvalidItemError("'{}'".format(item))

        for i in range(len(self.filters)):
            filter = self.filters[i]
            if filter["index"] == index + 1:
                if item is None:
                    del self.filters[i]
                else:
                    filter["name"] = item
                return

        # Otherwise its unique; add to list
        self.filters.append({"index": index + 1, "name": item})

    def set_item_filters(self, filters):
        # type: (list) -> None
        """
        Sets all of the item filters of the Entity.

        ``filters`` can be either of the following 2 formats::

            [{"index": int, "signal": item_name_1}, ...]
            # Or
            [item_name_1, item_name_2, ...]

        With the second format, the index of each item is set to it's position
        in the list. ``filters`` can also be ``None``, which will wipe all item
        filters that the Entity has.

        :param filters: The item filters to give the Entity.

        :exception DataFormatError: If the ``filters`` argument does not match
            the specification above.
        :exception IndexError: If the index of one of the entries exceeds or
            equals the ``filter_count`` of the Entity.
        :exception InvalidItemError: If the item name of one of the entries is
            not valid.
        """
        if filters is None:
            self.filters = None
            return

        # Normalize to standard internal format
        try:
            filters = signatures.FILTERS.validate(filters)
        except SchemaError as e:
            six.raise_from(DataFormatError(e), None)

        # Make sure the items are items and indices are within standards
        for item in filters:
            if item["index"] >= self.filter_count:
                raise IndexError(
                    "Index {} exceeds the maximum number of filter slots for this "
                    "entity ({})".format(item["index"], self.filter_count)
                )
            if item["name"] not in items.raw:
                raise InvalidItemError("'{}'".format(item))

        for item in filters:
            self.set_item_filter(item["index"] - 1, item["name"])
