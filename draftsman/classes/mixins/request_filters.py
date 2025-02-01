# request_filters.py

from draftsman.classes.exportable import attempt_and_reissue, test_replace_me
from draftsman.data import items
from draftsman.error import DataFormatError
from draftsman.signatures import DraftsmanBaseModel, RequestFilter, Section

from pydantic import BaseModel, Field, ValidationError, field_validator
from typing import Any, Optional, Union

from typing import TYPE_CHECKING

if TYPE_CHECKING:  # pragma: no coverage
    from draftsman.classes.entity import Entity


class RequestFiltersMixin:
    """
    Used to allow Logistics Containers to request items from the Logistic
    network.
    """

    class Format(BaseModel):
        class RequestFilters(DraftsmanBaseModel):
            sections: Optional[list[Section]] = Field(
                [], description="""The logistics groups requested to this spidertron."""
            )
            trash_not_requested: Optional[bool] = Field(
                False,
                description="""Moves any unrequested item to trash slots if enabled.""",
            )
            request_from_buffers: Optional[bool] = Field(
                True,
                description="""Whether or not to request from buffer chests. Always true.""",
            )
            enabled: Optional[bool] = Field(
                True,
                description="""Master switch to enable/disble logistics requests to this spidertron.""",
            )

        request_filters: Optional[RequestFilters] = RequestFilters()

        # request_filters: Optional[list[RequestFilter]] = Field(
        #     [],
        #     description="""
        #     Key which holds all of the logistics requests that this entity
        #     has.
        #     """,
        # )

        # @field_validator("request_filters", mode="before")
        # @classmethod
        # def normalize_validate(cls, value: Any):
        #     if isinstance(value, Sequence):
        #         result = []
        #         for i, entry in enumerate(value):
        #             if isinstance(entry, (list, tuple)):
        #                 result.append(
        #                     {"index": i + 1, "name": entry[0], "count": entry[1]}
        #                 )
        #             else:
        #                 result.append(entry)
        #         return result
        #     else:
        #         return value

    def __init__(self, name: str, similar_entities: list[str], **kwargs):
        self._root: __class__.Format

        super().__init__(name, similar_entities, **kwargs)

        self.request_filters = kwargs.get("request_filters", None)

    # =========================================================================

    # def set_request_filter(self, index: int, item: str, count: Optional[int] = None):
    #     """
    #     Sets the request filter at a particular index to request an amount of a
    #     certain item. Factorio imposes that an Entity can only have 1000 active
    #     requests at the same time.

    #     :param index: The index of the item request.
    #     :param item: The item name to request, or ``None``.
    #     :param count: The amount to request. If set to ``None``, it defaults to
    #         ``1``.

    #     :exception TypeError: If ``index`` is not an ``int``, ``item`` is not a
    #         ``str`` or ``None``, or ``count`` is not an ``int``.
    #     :exception InvalidItemError: If ``item`` is not a valid item name.
    #     :exception IndexError: If ``index`` is not in the range ``[0, 1000)``.
    #     """
    #     if item is not None:
    #         try:
    #             new_entry = RequestFilter(index=index, name=item, count=count)
    #             new_entry.index += 1
    #         except ValidationError as e:
    #             raise DataFormatError(e) from None

    #     new_filters = self.request_filters if self.request_filters is not None else []

    #     # Check to see if filters already contains an entry with the same index
    #     found_index = None
    #     for i, filter in enumerate(new_filters):
    #         if filter["index"] == index + 1:  # Index already exists in the list
    #             if item is None:  # Delete the entry
    #                 del new_filters[i]
    #             else:  # Set the new name + value
    #                 new_filters[i]["name"] = item
    #                 new_filters[i]["count"] = count
    #             found_index = i
    #             break

    #     # If no entry with the same index was found
    #     if found_index is None:
    #         new_filters.append(new_entry)

    #     result = attempt_and_reissue(
    #         self, type(self).Format, self._root, "request_filters", new_filters
    #     )
    #     self.request_filters = result

    # def set_request_filters(self, filters: list[tuple[str, int]]):
    #     """
    #     Sets all the request filters of the Entity in a shorthand format, where
    #     filters is of the format::

    #         [(item_1, count_1), (item_2, count_2), ...]

    #     where ``item_x`` is a ``str`` name and ``count_x`` is a positive integer.

    #     :param filters: The request filters to set.

    #     :exception DataFormatError: If ``filters`` does not match the format
    #         specified above.
    #     :exception InvalidItemError: If ``item_x`` is not a valid item name.
    #     """
    #     result = attempt_and_reissue(
    #         self, type(self).Format, self._root, "request_filters", filters
    #     )
    #     self._root.request_filters = result

    # def merge(self, other: "Entity"):
    #     super().merge(other)

    #     self.request_filters = other.request_filters

    # =========================================================================

    @property
    def request_filters(self) -> Optional[Format.RequestFilters]:
        """
        TODO
        """
        return self._root.request_filters

    @request_filters.setter
    def request_filters(self, value: Optional[Format.RequestFilters]) -> None:
        if self.validate_assignment:
            result = attempt_and_reissue(
                self,
                type(self).Format,
                self._root,
                "request_filters",
                value,
            )
            self._root.request_filters = result
        else:
            self._root.request_filters = value

    # =========================================================================

    @property
    def trash_not_requested(self) -> Optional[bool]:
        """
        TODO
        """
        return self.request_filters.trash_not_requested

    @trash_not_requested.setter
    def trash_not_requested(self, value: Optional[bool]) -> None:
        if self.validate_assignment:
            result = attempt_and_reissue(
                self,
                type(self).Format.RequestFilters,
                self.request_filters,
                "trash_not_requested",
                value,
            )
            self.request_filters.trash_not_requested = result
        else:
            self.request_filters.trash_not_requested = value

    # =========================================================================

    @property
    def request_from_buffers(self) -> Optional[bool]:
        """
        TODO
        """
        return self.request_filters.request_from_buffers

    @request_from_buffers.setter
    def request_from_buffers(self, value: Optional[bool]) -> None:
        if self.validate_assignment:
            result = attempt_and_reissue(
                self,
                type(self).Format.RequestFilters,
                self.request_filters,
                "request_from_buffers",
                value,
            )
            self.request_filters.request_from_buffers = result
        else:
            self.request_filters["request_from_buffers"] = value

    # =========================================================================

    @property
    def requests_enabled(self) -> Optional[bool]:
        """
        TODO
        """
        return self.request_filters.enabled

    @requests_enabled.setter
    def requests_enabled(self, value: Optional[bool]) -> None:
        if self.validate_assignment:
            result = attempt_and_reissue(
                self,
                type(self).Format.RequestFilters,
                self.request_filters,
                "enabled",
                value,
            )
            self.request_filters.enabled = result
        else:
            self.request_filters.enabled = value

    # =========================================================================

    @property
    def sections(self) -> Optional[list[Section]]:
        """
        TODO
        """
        return self.request_filters.sections

    @sections.setter
    def sections(self, value: Optional[list[Section]]) -> None:
        if self.validate_assignment:
            result = attempt_and_reissue(
                self,
                type(self).Format.RequestFilters,
                self.request_filters,
                "sections",
                value,
            )
            self.request_filters.sections = result
        else:
            self.request_filters.sections = value

    # =========================================================================

    def add_section(
        self,
        group: Union[str, None] = None,
        index: Optional[int] = None,  # TODO: integer size
        active: bool = True,
    ) -> Section:
        """
        Adds a new section of request/signal entries to the entity.

        NOTE:: Beware of giving sections the same or existing names! If a named
            group already exists within a save, then that group will take
            precedence over a newly added group.

        :param group: The name to give this group. The group will have no name
            if omitted.
        :param index: The index at which to insert the filter group. Defaults to
            the end if omitted.
        :param active: Whether or not this particular group is contributing its
            contents to the output in this specific combinator.

        :returns: A reference to the :class:`.Section` just added.
        """
        section = {"active": active}
        if group is not None:
            section["group"] = group
        if index is not None:
            section["index"] = index + 1
        else:
            section["index"] = len(self.sections) + 1
        section = Section(**section)
        self.sections.append(section)
        return self.sections[-1]

    # =========================================================================

    def __eq__(self, other) -> bool:
        return super().__eq__(other) and self.request_filters == other.request_filters
