# request_filters.py

from draftsman import signatures
from draftsman.data import signals
from draftsman.error import InvalidItemError, FilterIndexError

from schema import SchemaError


class RequestFiltersMixin(object):
    """
    Used to allow Logistics Containers to request items from the Logisitics
    network.
    """
    def __init__(self, name, similar_entities, **kwargs):
        # type: (str, list[str], **dict) -> None
        super(RequestFiltersMixin, self).__init__(
            name, similar_entities, **kwargs
        )

        # TODO: handle internal input format for set_request_filters()

        self.request_filters = None
        if "request_filters" in kwargs:
            self.set_request_filters(kwargs["request_filters"])
            self.unused_args.pop("request_filters")
        self._add_export("request_filters", lambda x: x is not None)

    # =========================================================================

    def set_request_filter(self, index, item, count = 0):
        # type: (int, str, int) -> None
        """
        """

        if self.request_filters is None:
            self.request_filters = []
        
        try:
            index = signatures.INTEGER.validate(index)
        except SchemaError:
            raise TypeError("Invalid index format")
        if item is not None and item not in signals.item: # TODO: FIXME
            raise InvalidItemError(item)
        count = signatures.INTEGER.validate(count)

        if not 0 <= index < 1000:
            raise FilterIndexError(
                "Filter index ({}) not in range [0, 1000)".format(index)
            )

        # Check to see if filters already contains an entry with the same index
        for i, filter in enumerate(self.request_filters):
            if filter["index"] == index + 1: # Index already exists in the list
                if item is None: # Delete the entry
                    del self.request_filters[i]
                else: # Set the new name + value
                    self.request_filters[i]["name"] = item
                    self.request_filters[i]["count"] = count
                return

        # If no entry with the same index was found
        self.request_filters.append({
            "index": index+1, "name": item, "count": count
        })

    def set_request_filters(self, filters):
        # type: (list) -> None
        """
        """

        # Validate filters
        # TODO: fix this signature
        filters = signatures.REQUEST_FILTERS.validate(filters)

        # Make sure the items are item signals
        for item in filters:
            if item[0] not in signals.item:
                raise InvalidItemError(item[0])

        # Make sure we dont wipe before throwing the error
        self.request_filters = []

        for i in range(len(filters)):
            self.set_request_filter(i, filters[i][0], filters[i][1])