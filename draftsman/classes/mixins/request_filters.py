# request_filters.py
# -*- encoding: utf-8 -*-

from __future__ import unicode_literals

from draftsman import signatures
from draftsman.data import items
from draftsman.error import InvalidItemError, DataFormatError

from schema import SchemaError
import six


class RequestFiltersMixin(object):
    """
    Used to allow Logistics Containers to request items from the Logistic
    network.
    """

    def __init__(self, name, similar_entities, **kwargs):
        # type: (str, list[str], **dict) -> None
        super(RequestFiltersMixin, self).__init__(name, similar_entities, **kwargs)

        self.request_filters = None

        if "request_filters" in kwargs:
            self.set_request_filters(kwargs["request_filters"])
            self.unused_args.pop("request_filters")
        self._add_export("request_filters", lambda x: x is not None)

    # =========================================================================

    def set_request_filter(self, index, item, count=None):
        # type: (int, str, int) -> None
        """
        Sets the request filter at a particular index to request an amount of a
        certain item. Factorio imposes that an Entity can only have 1000 active
        requests at the same time.

        :param index: The index of the item request.
        :param item: The item name to request, or ``None``.
        :param count: The amount to request. If set to ``None``, it defaults to
            the stack size of ``item``.

        :exception TypeError: If ``index`` is not an ``int``, ``item`` is not a
            ``str`` or ``None``, or ``count`` is not an ``int``.
        :exception InvalidItemError: If ``item`` is not a valid item name.
        :exception IndexError: If ``index`` is not in the range ``[0, 1000)``.
        """
        try:
            index = signatures.INTEGER.validate(index)
            item = signatures.STRING_OR_NONE.validate(item)
            count = signatures.INTEGER_OR_NONE.validate(count)
        except SchemaError as e:
            six.raise_from(TypeError(e), None)

        if item is not None and item not in items.raw:
            raise InvalidItemError("'{}'".format(item))
        if not 0 <= index < 1000:
            raise IndexError("Filter index ({}) not in range [0, 1000)".format(index))
        if count is None:  # default count to the item's stack size
            count = 0 if item is None else items.raw[item]["stack_size"]
        if count < 0:
            raise ValueError("Filter count ({}) must be positive".format(count))

        if self.request_filters is None:
            self.request_filters = []

        # Check to see if filters already contains an entry with the same index
        for i, filter in enumerate(self.request_filters):
            if filter["index"] == index + 1:  # Index already exists in the list
                if item is None:  # Delete the entry
                    del self.request_filters[i]
                else:  # Set the new name + value
                    self.request_filters[i]["name"] = item
                    self.request_filters[i]["count"] = count
                return

        # If no entry with the same index was found
        self.request_filters.append({"index": index + 1, "name": item, "count": count})

    def set_request_filters(self, filters):
        # type: (list) -> None
        """
        Sets all the request filters of the Entity, where filters is of the
        format::

            [(item_1, count_1), (item_2, count_2), ...]

        where ``item_x`` is a ``str`` name and ``count_x`` is a positive integer.

        :param filters: The request filters to set.

        :exception DataFormatError: If ``filters`` does not match the format
            specified above.
        :exception InvalidItemError: If ``item_x`` is not a valid item name.
        """
        # Validate filters
        try:
            filters = signatures.REQUEST_FILTERS.validate(filters)
        except SchemaError as e:
            six.raise_from(DataFormatError(e), None)

        # Make sure the items are items
        for item in filters:
            if item["name"] not in items.raw:
                raise InvalidItemError(item["name"])

        self.request_filters = []
        for i in range(len(filters)):
            self.set_request_filter(i, filters[i]["name"], filters[i]["count"])
