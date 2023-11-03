# filters.py

from draftsman.classes.exportable import attempt_and_reissue
from draftsman.data import items, entities
from draftsman.error import InvalidItemError, DataFormatError
from draftsman.signatures import DraftsmanBaseModel, Filters, SignalID, int64

from pydantic import Field, ValidationError, ValidationInfo, validate_call
from typing import Optional
import six


class FiltersMixin:
    """
    Allows the entity to specify item filters.
    """

    class Format(DraftsmanBaseModel):
        filters: Optional[Filters] = Field(
            Filters(),
            description="""
            Any item filters that this inserter or loader has.
            """,
        )

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

        :type: ``int``
        """
        return entities.raw.get(self.name, {"filter_count": None}).get(
            "filter_count", 0
        )

    @property
    def filters(self) -> Filters:
        """
        TODO
        """
        return self._root.filters

    @filters.setter
    def filters(self, value: Filters):
        if self.validate_assignment:
            result = attempt_and_reissue(
                self, type(self).Format, self._root, "filters", value
            )
            self._root.filters = result
        else:
            self._root.filters = value

    # =========================================================================

    def set_item_filter(self, index: int64, item: str):  # TODO: SignalName
        """
        Sets one of the item filters of the Entity. `index` in this function is
        in 0-based notation.

        :param index: The index of the filter to set.
        :param item: The string name of the item to filter.

        :exception IndexError: If ``index`` is set to a value exceeding or equal
            to ``filter_count``.
        :exception InvalidItemError: If ``item`` is not a valid item name.
        """
        # Check if index is ouside the range of the max filter slots
        if index >= self.filter_count:
            raise IndexError(
                "Index {} exceeds the maximum number of filter slots for this "
                "entity ({})".format(index, self.filter_count)
            )

        if item is not None and item not in items.raw:
            raise InvalidItemError("'{}'".format(item))

        if self.filters is None:
            self.filters = Filters()

        for i in range(len(self.filters.root)):
            filter = self.filters.root[i]
            if filter["index"] == index + 1:
                if item is None:
                    del self.filters.root[i]
                else:
                    filter["name"] = item
                return

        # Otherwise its unique; add to list
        self.filters.root.append(Filters.FilterEntry(index=index + 1, name=item))

    # def set_item_filters(self, filters):  # TODO: remove(?)
    #     # type: (list) -> None
    #     """
    #     Sets all of the item filters of the Entity.

    #     ``filters`` can be either of the following 2 formats::

    #         [{"index": int, "name": item_name_1}, ...]
    #         # Or
    #         [item_name_1, item_name_2, ...]

    #     With the first format, the "index" key is in 1-based notation.
    #     With the second format, the index of each item is set to it's position
    #     in the list. ``filters`` can also be ``None``, which will wipe all item
    #     filters that the Entity has.

    #     :param filters: The item filters to give the Entity.

    #     :exception DataFormatError: If the ``filters`` argument does not match
    #         the specification above.
    #     :exception IndexError: If the index of one of the entries exceeds or
    #         equals the ``filter_count`` of the Entity.
    #     :exception InvalidItemError: If the item name of one of the entries is
    #         not valid.
    #     """
    #     if filters is None:
    #         self.filters = None
    #         return

    #     # Normalize to standard internal format
    #     try:
    #         filters = Filters(filters).model_dump(
    #             by_alias=True, exclude_none=True, exclude_defaults=True
    #         )
    #     except ValidationError as e:
    #         six.raise_from(DataFormatError(e), None)

    #     # Make sure the items are items and indices are within standards
    #     for item in filters:
    #         if item["index"] > self.filter_count:
    #             raise IndexError(
    #                 "Index {} exceeds the maximum number of filter slots for this "
    #                 "entity ({})".format(item["index"], self.filter_count)
    #             )
    #         if item["name"] not in items.raw:
    #             raise InvalidItemError("'{}'".format(item))

    #     for item in filters:
    #         self.set_item_filter(item["index"] - 1, item["name"])

    # =========================================================================

    def merge(self, other):
        super().merge(other)

        self.filters = other.filters
        # for item in other.filters:
        #     self.set_item_filter(item["index"] - 1, item["name"])

    # =========================================================================

    def __eq__(self, other) -> bool:
        return super().__eq__(other) and self.filters == other.filters
