# filters.py

from draftsman.data import signals
from draftsman.error import InvalidItemError


class FiltersMixin(object):
    """
    TODO
    """
    def __init__(self, name, similar_entities, **kwargs):
        # type: (str, list[str], **dict) -> None
        super(FiltersMixin, self).__init__(name, similar_entities, **kwargs)

        self.filters = None
        if "filters" in kwargs:
            self.set_item_filters(kwargs["filters"])
            self.unused_args.pop("filters")
        self._add_export("filters", lambda x: x is not None and len(x) != 0)

    # =========================================================================

    def set_item_filter(self, index, item):
        # type: (int, str) -> None
        """
        """
        if self.filters is None:
            self.filters = []

        # TODO: check if index is ouside the range of the max filter slots
        # (which needs to be extracted)

        if item is not None and item not in signals.item:
            raise InvalidItemError(item)

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
        Sets the item filters for the inserter or loader.
        """
        if filters is None:
            self.filters = None
            return

        # Make sure the items are item signals
        for item in filters:
            if isinstance(item, dict):
                item = item["name"]
            if item not in signals.item: # TODO: FIXME?
                raise InvalidItemError(item)

        for i in range(len(filters)):
            if isinstance(filters[i], str):
                self.set_item_filter(i, filters[i])
            else: # dict
                self.set_item_filter(i, filters[i]["name"])