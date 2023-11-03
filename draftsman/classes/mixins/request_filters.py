# request_filters.py

from draftsman.classes.exportable import attempt_and_reissue
from draftsman.signatures import RequestFilters
from draftsman.data import items
from draftsman.error import InvalidItemError, DataFormatError

from pydantic import BaseModel, Field, ValidationError, validate_call
import six
from typing import Optional

from typing import TYPE_CHECKING

if TYPE_CHECKING:  # pragma: no coverage
    from draftsman.classes.entity import Entity


class RequestFiltersMixin:
    """
    Used to allow Logistics Containers to request items from the Logistic
    network.
    """

    class Format(BaseModel):
        request_filters: Optional[RequestFilters] = Field(
            RequestFilters([]),
            description="""
            Key which holds all of the logistics requests that this entity
            has.
            """,
        )

    def __init__(self, name: str, similar_entities: list[str], **kwargs):
        self._root: __class__.Format

        super().__init__(name, similar_entities, **kwargs)

        self.request_filters = kwargs.get("request_filters", None)

    # =========================================================================

    @property
    def request_filters(self) -> RequestFilters:
        """
        TODO
        """
        return self._root.request_filters

    @request_filters.setter
    def request_filters(self, value: RequestFilters):
        if self.validate_assignment:
            result = attempt_and_reissue(
                self, type(self).Format, self._root, "request_filters", value
            )
            self._root.request_filters = result
        else:
            self._root.request_filters = value

    # =========================================================================

    def set_request_filter(self, index: int, item: str, count: Optional[int] = None):
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
        # try: # TODO
        #     index = signatures.INTEGER.validate(index)
        #     item = signatures.STRING_OR_NONE.validate(item)
        #     count = signatures.INTEGER_OR_NONE.validate(count)
        # except SchemaError as e:
        #     six.raise_from(TypeError(e), None)

        # if item is not None and item not in items.raw:
        #     raise InvalidItemError("'{}'".format(item))
        # if not 0 <= index < 1000:
        #     raise IndexError("Filter index ({}) not in range [0, 1000)".format(index))
        if count is None:  # get item's stack size
            count = items.raw.get(item, {}).get("stack_size", 0)
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

    @validate_call
    def set_request_filters(
        self, filters: list[tuple[str, int]]
    ):  # TODO: int dimension
        """
        Sets all the request filters of the Entity in a shorthand format, where
        filters is of the format::

            [(item_1, count_1), (item_2, count_2), ...]

        where ``item_x`` is a ``str`` name and ``count_x`` is a positive integer.

        :param filters: The request filters to set.

        :exception DataFormatError: If ``filters`` does not match the format
            specified above.
        :exception InvalidItemError: If ``item_x`` is not a valid item name.
        """
        # Validate filters
        try:
            filters = RequestFilters(root=filters)
        except ValidationError as e:
            six.raise_from(DataFormatError(e), None)

        # Make sure the items are items
        # for item in filters:
        #     if item["name"] not in items.raw:
        #         raise InvalidItemError(item["name"])

        self._root.request_filters = filters

    def merge(self, other: "Entity"):
        super().merge(other)

        self.request_filters = other.request_filters

    # =========================================================================

    def __eq__(self, other) -> bool:
        return super().__eq__(other) and self.request_filters == other.request_filters
