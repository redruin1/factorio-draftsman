# filters.py

from draftsman.classes.exportable import attempt_and_reissue, test_replace_me
from draftsman.data import items, entities
from draftsman.error import InvalidItemError, DataFormatError
from draftsman.serialization import draftsman_converters
from draftsman.signatures import (
    DraftsmanBaseModel,
    ItemFilter,
    AttrsItemFilter,
    ItemName,
    int64,
)
from draftsman.validators import instance_of

import attrs
from pydantic import Field, ValidationError, ValidationInfo, field_validator
from typing import Any, Literal, Optional


@attrs.define(slots=False)
class FiltersMixin:
    """
    Allows the entity to specify item filters.
    """

    # class Format(DraftsmanBaseModel):
    #     use_filters: Optional[bool] = Field(
    #         False,
    #         description="""
    #         Whether or not this inserter should use filters
    #         """,
    #     )
    #     filters: Optional[list[ItemFilter]] = Field(
    #         [],
    #         description="""
    #         Any item filters that this inserter or loader has.
    #         """,
    #     )

    #     @field_validator("filters", mode="before")
    #     @classmethod
    #     def normalize_filters(cls, value: Any):
    #         if isinstance(value, (list, tuple)):
    #             result = []
    #             for i, entry in enumerate(value):
    #                 if isinstance(entry, str):
    #                     result.append({"index": i + 1, "name": entry})
    #                 else:
    #                     result.append(entry)
    #             return result
    #         else:
    #             return value

    # def __init__(self, name: str, similar_entities: list[str], **kwargs):
    #     self._root: __class__.Format

    #     super().__init__(name, similar_entities, **kwargs)

    #     self.filters = kwargs.get("filters", None)

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

    # =========================================================================

    use_filters: bool = attrs.field(default=False, validator=instance_of(bool))
    """
    Whether or not this inserter should use filters at all. Overrided by
    ``circuit_set_filters``, if present.
    """

    # @property
    # def use_filters(self) -> Optional[bool]:
    #     """
    #     Whether or not this inserter should use filters at all. Overrided by
    #     ``circuit_set_filters``, if present.
    #     """
    #     return self._root.use_filters

    # @use_filters.setter
    # def use_filters(self, value: Optional[list[ItemFilter]]):
    #     test_replace_me(
    #         self,
    #         type(self).Format,
    #         self._root,
    #         "use_filters",
    #         value,
    #         self.validate_assignment,
    #     )

    # =========================================================================

    def _filters_converter(value):
        if isinstance(value, list):
            for i, elem in enumerate(value):
                value[i] = AttrsItemFilter.converter(elem)
            return value
        else:
            return value

    filters: list[ItemFilter] = attrs.field(
        factory=list,
        converter=_filters_converter,
        validator=instance_of(list),  # TODO: more validators
    )
    """
    The manually-set item filters that this inserter/loader will abide by. These
    values are overridden by filters set by the circuit network, if so 
    configured.
    """

    # @property
    # def filters(self) -> Optional[list[ItemFilter]]:
    #     """
    #     TODO
    #     """
    #     return self._root.filters

    # @filters.setter
    # def filters(self, value: Optional[list[ItemFilter]]):
    #     test_replace_me(
    #         self,
    #         type(self).Format,
    #         self._root,
    #         "filters",
    #         value,
    #         self.validate_assignment,
    #     )
    #     # if self.validate_assignment:
    #     #     result = attempt_and_reissue(
    #     #         self, type(self).Format, self._root, "filters", value
    #     #     )
    #     #     self._root.filters = result
    #     # else:
    #     #     self._root.filters = value

    # =========================================================================

    def set_item_filter(
        self,
        index: int64,
        item: ItemName,
        quality: Literal[
            "normal", "uncommon", "rare", "epic", "legendary", "any"
        ] = "normal",
        comparator: Literal[">", "<", "=", "==", "≥", ">=", "≤", "<=", "≠", "!="] = "=",
    ):
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
            new_entry = AttrsItemFilter(
                index=index, name=item, quality=quality, comparator=comparator
            )

        found_index = None
        for i in range(len(self.filters)):
            filter = self.filters[i]
            if filter.index == index + 1:
                if item is None:
                    del self.filters[i]
                else:
                    filter.name = item
                    filter.quality = quality
                    filter.comparator = comparator
                found_index = i
                break

        if found_index is None:
            # TODO: bisect
            self.filters.append(new_entry)

    # def set_item_filters(self, *filters: Optional[list[ItemFilter]]):
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
    #     # Passing None into the function wraps it in a tuple, which we undo here
    #     if len(filters) == 1 and filters[0] is None:
    #         filters = None

    #     result = attempt_and_reissue(
    #         self, type(self).Format, self._root, "filters", filters
    #     )
    #     self._root.filters = result

    # =========================================================================

    def merge(self, other: "FiltersMixin"):
        super().merge(other)

        self.filters = other.filters

    # =========================================================================

    # def __eq__(self, other: "FiltersMixin") -> bool:
    #     return super().__eq__(other) and self.filters == other.filters


draftsman_converters.add_schema(
    {"$id": "factorio:item_filters_mixin"},
    FiltersMixin,
    lambda fields: {
        "use_filters": fields.use_filters.name,
        "filters": fields.filters.name,
    },
    lambda fields, converter: {
        "use_filters": fields.use_filters.name,
        "filters": (fields.filters, lambda inst: [converter.unstructure(e) for e in inst.filters]),
    }
)
