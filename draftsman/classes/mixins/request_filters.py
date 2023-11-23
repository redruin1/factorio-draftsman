# request_filters.py

from draftsman.classes.exportable import attempt_and_reissue
from draftsman.data import items
from draftsman.error import DataFormatError
from draftsman.signatures import RequestFilter

from pydantic import BaseModel, Field, ValidationError, field_validator
from typing import Any, Optional, Sequence

from typing import TYPE_CHECKING

if TYPE_CHECKING:  # pragma: no coverage
    from draftsman.classes.entity import Entity


class RequestFiltersMixin:
    """
    Used to allow Logistics Containers to request items from the Logistic
    network.
    """

    class Format(BaseModel):
        request_filters: Optional[list[RequestFilter]] = Field(
            [],
            description="""
            Key which holds all of the logistics requests that this entity
            has.
            """,
        )

        @field_validator("request_filters", mode="before")
        @classmethod
        def normalize_validate(cls, value: Any):
            if isinstance(value, Sequence):
                result = []
                for i, entry in enumerate(value):
                    if isinstance(entry, (list, tuple)):
                        result.append(
                            {"index": i + 1, "name": entry[0], "count": entry[1]}
                        )
                    else:
                        result.append(entry)
                return result
            else:
                return value

    def __init__(self, name: str, similar_entities: list[str], **kwargs):
        self._root: __class__.Format

        super().__init__(name, similar_entities, **kwargs)

        self.request_filters = kwargs.get("request_filters", None)

    # =========================================================================

    @property
    def request_filters(self) -> Optional[list[RequestFilter]]:
        """
        TODO
        """
        return self._root.request_filters

    @request_filters.setter
    def request_filters(self, value: Optional[list[RequestFilter]]):
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
            ``1``.

        :exception TypeError: If ``index`` is not an ``int``, ``item`` is not a
            ``str`` or ``None``, or ``count`` is not an ``int``.
        :exception InvalidItemError: If ``item`` is not a valid item name.
        :exception IndexError: If ``index`` is not in the range ``[0, 1000)``.
        """
        if item is not None:
            try:
                new_entry = RequestFilter(index=index, name=item, count=count)
                new_entry.index += 1
            except ValidationError as e:
                raise DataFormatError(e) from None

        new_filters = self.request_filters if self.request_filters is not None else []

        # Check to see if filters already contains an entry with the same index
        found_index = None
        for i, filter in enumerate(new_filters):
            if filter["index"] == index + 1:  # Index already exists in the list
                if item is None:  # Delete the entry
                    del new_filters[i]
                else:  # Set the new name + value
                    new_filters[i]["name"] = item
                    new_filters[i]["count"] = count
                found_index = i
                break

        # If no entry with the same index was found
        if found_index is None:
            new_filters.append(new_entry)

        result = attempt_and_reissue(
            self, type(self).Format, self._root, "request_filters", new_filters
        )
        self.request_filters = result

    def set_request_filters(self, filters: list[tuple[str, int]]):
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
        result = attempt_and_reissue(
            self, type(self).Format, self._root, "request_filters", filters
        )
        self._root.request_filters = result

    def merge(self, other: "Entity"):
        super().merge(other)

        self.request_filters = other.request_filters

    # =========================================================================

    def __eq__(self, other) -> bool:
        return super().__eq__(other) and self.request_filters == other.request_filters
