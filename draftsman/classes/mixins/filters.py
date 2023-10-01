# filters.py
# -*- encoding: utf-8 -*-

from __future__ import unicode_literals

from draftsman.data import items, entities
from draftsman.error import InvalidItemError, DataFormatError
from draftsman.signatures import Filters

from pydantic import BaseModel, ValidationError
import six


class FiltersMixin(object):
    """
    Allows the entity to specify item filters.
    """

    # _exports = {
    #     "filters": {
    #         "format": "[{'index': int, 'name': item_name_1}, ...]",
    #         "description": "Any item filters that this entity has",
    #         "required": lambda x: x is not None and len(x) != 0,
    #     }
    # }
    class Format(BaseModel):
        filters: Filters | None = None

    def __init__(self, name, similar_entities, **kwargs):
        # type: (str, list[str], **dict) -> None
        super(FiltersMixin, self).__init__(name, similar_entities, **kwargs)

        self._filter_count = entities.raw[self.name].get("filter_count", 0) # TODO: memory savings

        self.filters = None

        if "filters" in kwargs:
            self.filters = kwargs["filters"]
            self.unused_args.pop("filters")
        # self._add_export("filters", lambda x: x is not None and len(x) != 0)

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
    

    @property
    def filters(self):
        # TODO
        """
        TODO
        """
        return self._root.get("filters", None)
    
    @filters.setter
    def filters(self, value):
        # TODO
        if value is None:
            self._root.pop("filters", None)
        else:
            self._root["filters"] = value

    # =========================================================================

    def set_item_filter(self, index, item):
        # type: (int, str) -> None
        """
        Sets one of the item filters of the Entity. `index` in this function is
        in 0-based notation.

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

            [{"index": int, "name": item_name_1}, ...]
            # Or
            [item_name_1, item_name_2, ...]

        With the first format, the "index" key is in 1-based notation.
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
            filters = Filters(filters).model_dump(by_alias=True, exclude_none=True, exclude_defaults=True)
        except ValidationError as e:
            six.raise_from(DataFormatError(e), None)

        print(filters)

        # Make sure the items are items and indices are within standards
        for item in filters:
            if item["index"] > self.filter_count:
                raise IndexError(
                    "Index {} exceeds the maximum number of filter slots for this "
                    "entity ({})".format(item["index"], self.filter_count)
                )
            if item["name"] not in items.raw:
                raise InvalidItemError("'{}'".format(item))

        for item in filters:
            self.set_item_filter(item["index"] - 1, item["name"])

    # =========================================================================

    def merge(self, other):
        super(FiltersMixin, self).merge(other)

        self.filters = []
        for item in other.filters:
            self.set_item_filter(item["index"] - 1, item["name"])

    # =========================================================================

    def __eq__(self, other) -> bool:
        return super().__eq__(other) and self.filters == other.filters
