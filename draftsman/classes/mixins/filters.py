# filters.py

from draftsman.classes.exportable import attempt_and_reissue, test_replace_me
from draftsman.data import items, entities
from draftsman.error import InvalidItemError, DataFormatError
from draftsman.signatures import DraftsmanBaseModel, FilterEntry, ItemName, int64

from pydantic import Field, ValidationError, ValidationInfo, field_validator
from typing import Any, Optional


class FiltersMixin:
    """
    Allows the entity to specify item filters.
    """

    class Format(DraftsmanBaseModel):
        filters: Optional[list[FilterEntry]] = Field(
            [],
            description="""
            Any item filters that this inserter or loader has.
            """,
        )

        @field_validator("filters", mode="before")
        @classmethod
        def normalize_filters(cls, value: Any):
            if isinstance(value, (list, tuple)):
                result = []
                for i, entry in enumerate(value):
                    if isinstance(entry, str):
                        result.append({"index": i + 1, "name": entry})
                    else:
                        result.append(entry)
                return result
            else:
                return value

    def __init__(self, name: str, similar_entities: list[str], **kwargs):
        self._root: __class__.Format

        super().__init__(name, similar_entities, **kwargs)

        self.filters = kwargs.get("filters", None)

    # =========================================================================

    @property
    def filter_count(self) -> Optional[int]:
        """
        The number of filter slots that this Entity has in total. Equivalent to
        the ``"filter_count"`` key in Factorio's ``data.raw``. Returns ``None``
        if this entity's name is not recognized by Draftsman. Not exported; read
        only.
        """
        return entities.raw.get(self.name, {"filter_count": None}).get(
            "filter_count", 0
        )

    @property
    def filters(self) -> Optional[list[FilterEntry]]:
        """
        TODO
        """
        return self._root.filters

    @filters.setter
    def filters(self, value: Optional[list[FilterEntry]]):
        test_replace_me(
            self,
            type(self).Format,
            self._root,
            "filters",
            value,
            self.validate_assignment,
        )
        # if self.validate_assignment:
        #     result = attempt_and_reissue(
        #         self, type(self).Format, self._root, "filters", value
        #     )
        #     self._root.filters = result
        # else:
        #     self._root.filters = value

    # =========================================================================

    def set_item_filter(self, index: int64, item: ItemName):
        """
        Sets one of the item filters of the Entity. `index` in this function is
        in 0-based notation.

        :param index: The index of the filter to set.
        :param item: The string name of the item to filter.

        :exception IndexError: If ``index`` is set to a value exceeding or equal
            to ``filter_count``.
        :exception InvalidItemError: If ``item`` is not a valid item name.
        """
        if item is not None:
            try:
                new_entry = FilterEntry(index=index, name=item)
                new_entry.index += 1
            except ValidationError as e:
                raise DataFormatError(e) from None

        new_filters = self.filters if self.filters is not None else []

        found_index = None
        for i in range(len(new_filters)):
            filter = new_filters[i]
            if filter["index"] == index + 1:
                if item is None:
                    del new_filters[i]
                else:
                    filter["name"] = item
                found_index = i
                break

        if found_index is None:
            new_filters.append(new_entry)

        result = attempt_and_reissue(
            self, __class__.Format, self._root, "filters", new_filters
        )
        self.filters = result

    def set_item_filters(self, *filters: Optional[list[FilterEntry]]):
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
        # Passing None into the function wraps it in a tuple, which we undo here
        if len(filters) == 1 and filters[0] is None:
            filters = None

        result = attempt_and_reissue(
            self, type(self).Format, self._root, "filters", filters
        )
        self._root.filters = result

    # =========================================================================

    def merge(self, other: "FiltersMixin"):
        super().merge(other)

        self.filters = other.filters

    # =========================================================================

    def __eq__(self, other: "FiltersMixin") -> bool:
        return super().__eq__(other) and self.filters == other.filters
