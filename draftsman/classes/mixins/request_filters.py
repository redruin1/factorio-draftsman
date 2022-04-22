# request_filters.py
# -*- encoding: utf-8 -*-

from __future__ import unicode_literals

from draftsman import signatures
from draftsman.data import items
from draftsman.error import InvalidItemError, FilterIndexError, DataFormatError

from schema import SchemaError
import six


class RequestFiltersMixin(object):
    """
    Used to allow Logistics Containers to request items from the Logisitics
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

    def set_request_filter(self, index, item, count=0):
        # type: (int, str, int) -> None
        """ """

        if self.request_filters is None:
            self.request_filters = []

        if not isinstance(index, six.integer_types):
            raise TypeError("'index' must be an int")
        if item is not None and item not in items.raw:
            raise InvalidItemError(item)
        if not isinstance(count, six.integer_types):
            raise TypeError("'count' must be an int")

        if not 0 <= index < 1000:
            raise FilterIndexError(
                "Filter index ({}) not in range [0, 1000)".format(index)
            )

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
        """ """

        # Validate filters
        try:
            filters = signatures.REQUEST_FILTERS.validate(filters)
        except SchemaError as e:
            six.raise_from(DataFormatError(e), None)

        # Make sure the items are items
        for item in filters:
            if item[0] not in items.raw:
                raise InvalidItemError(item[0])

        self.request_filters = []
        for i in range(len(filters)):
            self.set_request_filter(i, filters[i][0], filters[i][1])
