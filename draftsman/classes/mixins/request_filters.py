# request_filters.py

from draftsman.classes.exportable import attempt_and_reissue, test_replace_me
from draftsman.data import items
from draftsman.data.signals import get_signal_types
from draftsman.error import InvalidSignalError
from draftsman.serialization import draftsman_converters
from draftsman.signatures import (
    DraftsmanBaseModel,
    RequestFilter,
    Section,
    SignalFilter,
    int32,
    int64,
    uint32,
)

import attrs
import cattrs
from pydantic import BaseModel, Field, ValidationError, field_validator
from typing import Any, Literal, Optional, Union

from typing import TYPE_CHECKING

if TYPE_CHECKING:  # pragma: no coverage
    from draftsman.classes.entity import Entity


@attrs.define
class AttrsSignalFilter:
    index: int64 = attrs.field(
        # TODO: validators
    )
    """
    Numeric index of the signal in the combinator, 1-based. Typically the 
    index of the signal in the parent 'filters' key, but this is not 
    strictly enforced. 
    """
    name: str = attrs.field(  # TODO: SignalName
        # TODO: validators
    )
    """
    Name of the signal.
    """
    count: int32 = attrs.field()
    """
    Value of the signal filter, or the lower bound of a range if ``max_count`` 
    is also specified.
    """
    type: Optional[
        Literal[
            "virtual",
            "item",
            "fluid",
            "recipe",
            "entity",
            "space-location",
            "asteroid-chunk",
            "quality",
        ]
    ] = attrs.field(
        # TODO: validators
    )
    """
    Type of the signal.
    """

    @type.default
    def get_type_default(
        self,
    ) -> Literal[
        "virtual",
        "item",
        "fluid",
        "recipe",
        "entity",
        "space-location",
        "asteroid-chunk",
        "quality",
    ]:
        try:
            return next(iter(get_signal_types(self.name)))
        except InvalidSignalError:
            return "item"

    # signal: Optional[SignalID] = Field(
    #     None,
    #     description="""
    #     Signal to broadcast. If this value is omitted the occupied slot will
    #     behave as if no signal exists within it. Cannot be a pure virtual
    #     (logic) signal like "signal-each", "signal-any", or
    #     "signal-everything"; if such signals are set they will be removed
    #     on import.
    #     """,
    # )
    # TODO: make this dynamic based on current environment?
    quality: Literal[
        "normal", "uncommon", "rare", "epic", "legendary", "quality-unknown", "any"
    ] = attrs.field(
        default="any",
        # TODO: validators
    )
    """
    Quality flag of the signal. If unspecified, this value is effectively 
    equal to 'any' quality level.
    """
    comparator: Literal[">", "<", "=", "≥", "≤", "≠"] = attrs.field(
        default="=",
        # TODO: converter from double forms
        # TODO: validators
    )
    """
    Comparison operator when deducing the quality type.
    """
    max_count: Optional[int32] = attrs.field(
        default=None,
        # TODO: validators
    )
    """
    The maximum amount of the signal to request of the signal to emit. Only used
    (currently) with logistics-type requests.
    """

    # Deprecated in 2.0
    # @field_validator("index")
    # @classmethod
    # def ensure_index_within_range(cls, value: int64, info: ValidationInfo):
    #     """
    #     Factorio does not permit signal values outside the range of it's item
    #     slot count; this method raises an error IF item slot count is known.
    #     """
    #     if not info.context:
    #         return value
    #     if info.context["mode"] <= ValidationMode.MINIMUM:
    #         return value

    #     entity = info.context["object"]

    #     # If Draftsman doesn't recognize entity, early exit
    #     if entity.item_slot_count is None:
    #         return value

    #     # TODO: what happens if index is 0?
    #     if not 0 < value <= entity.item_slot_count:
    #         raise ValueError(
    #             "Signal 'index' ({}) must be in the range [0, {})".format(
    #                 value, entity.item_slot_count
    #             )
    #         )

    #     return value

    # TODO: move to ConstantCombinator
    # @field_validator("name")
    # @classmethod
    # def ensure_not_pure_virtual(cls, value: Optional[str], info: ValidationInfo):
    #     """
    #     Warn if pure virtual signals (like "signal-each", "signal-any", and
    #     "signal-everything") are entered inside of a constant combinator.
    #     """
    #     if not info.context or value is None:
    #         return value
    #     if info.context["mode"] <= ValidationMode.MINIMUM:
    #         return value

    #     warning_list: list = info.context["warning_list"]

    #     if value in pure_virtual:
    #         warning_list.append(
    #             PureVirtualDisallowedWarning(
    #                 "Cannot set pure virtual signal '{}' in a constant combinator".format(
    #                     value.name
    #                 )
    #             )
    #         )

    #     return value


@attrs.define
class AttrsSection:
    index: uint32 = attrs.field(
        # TODO: validators
    )  # TODO: 0-based or 1-based?
    """
    Location of the logistics section within the entity, 1-indexed.
    """

    def filters_converter(self, value: list[Any]) -> list[AttrsSignalFilter]:
        # TODO: more robust testing
        if isinstance(value, list):
            for i, entry in enumerate(value):
                if isinstance(entry, tuple):
                    value[i] = AttrsSignalFilter(
                        index=i + 1,
                        name=entry[0],
                        count=entry[1],
                    )

        return value

    filters: list[AttrsSignalFilter] = attrs.field(
        factory=list,
        # converter=filters_converter
        # TODO: validators
    )
    """
    List of item requests for this section.
    """

    group: Optional[str] = attrs.field(
        default=None,
        # TODO: validators
    )
    """
    Name of this section group. Once named, this group will become registered 
    within the save it is imported into. If a logistic section with the given
    name already exists within the save, the one that exists in the save will 
    overwrite the one specified here.
    """

    def set_signal(
        self,
        index: int64,
        name: Union[str, None],
        count: int32 = 0,
        quality: Literal[
            "normal",
            "uncommon",
            "rare",
            "epic",
            "legendary",
            "quality-unknown",
            "any",
        ] = "normal",
        type: Optional[str] = None,
    ) -> None:
        new_entry = AttrsSignalFilter(
            index=index,
            name=name,
            type=type,
            quality=quality,
            comparator="=",
            count=count,
        )

        # Check to see if filters already contains an entry with the same index
        existing_index = None
        for i, signal_filter in enumerate(self.filters):
            if index + 1 == signal_filter["index"]:  # Index already exists in the list
                if name is None:  # Delete the entry
                    del self.filters[i]
                else:
                    self.filters[i] = new_entry
                existing_index = i
                break

        if existing_index is None:
            self.filters.append(new_entry)

    def get_signal(self, index: int64) -> Optional[AttrsSignalFilter]:
        """
        Get the :py:data:`.SIGNAL_FILTER` ``dict`` entry at a particular index,
        if it exists.

        :param index: The index of the signal to analyze.

        :returns: A ``dict`` that conforms to :py:data:`.SIGNAL_FILTER`, or
            ``None`` if nothing was found at that index.
        """
        return next(
            (item for item in self.filters if item["index"] == index + 1),
            None,
        )

    # @field_validator("filters", mode="before")
    # @classmethod
    # def normalize_input(cls, value: Any):
    #     if isinstance(value, list):
    #         for i, entry in enumerate(value):
    #             if isinstance(entry, tuple):
    #                 # TODO: perhaps it would be better to modify the format so
    #                 # you must specify the signal type... or maybe not...
    #                 signal_types = get_signal_types(entry[0])
    #                 filter_type = (
    #                     "item" if "item" in signal_types else next(iter(signal_types))
    #                 )
    #                 value[i] = {
    #                     "index": i + 1,
    #                     "name": entry[0],
    #                     "type": filter_type,
    #                     "comparator": "=",
    #                     "count": entry[1],
    #                 }

    #     return value


@attrs.define(slots=False)
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
                description="""Whether or not to request from buffer chests.""",
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

    # def __init__(self, name: str, similar_entities: list[str], **kwargs):
    #     self._root: __class__.Format

    #     super().__init__(name, similar_entities, **kwargs)

    #     self.request_filters = kwargs.get("request_filters", None)

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

    # =========================================================================

    # request_filters: RequestFilters = attrs.field(
    #     factory=RequestFilters,
    #     converter=RequestFilters,
    #     validator=attrs.validators.instance_of(RequestFilters),
    # )
    # """
    # TODO
    # """

    # @property
    # def request_filters(self) -> Optional[Format.RequestFilters]:
    #     """
    #     TODO
    #     """
    #     return self._root.request_filters

    # @request_filters.setter
    # def request_filters(self, value: Optional[Format.RequestFilters]) -> None:
    #     # if self.validate_assignment:
    #     #     result = attempt_and_reissue(
    #     #         self,
    #     #         type(self).Format,
    #     #         self._root,
    #     #         "request_filters",
    #     #         value,
    #     #     )
    #     #     self._root.request_filters = result
    #     # else:
    #     #     self._root.request_filters = value
    #     result = attempt_and_reissue(
    #         self, type(self).Format, self._root, "request_filters", value
    #     )
    #     self._root.request_filters = result

    # =========================================================================

    trash_not_requested: bool = attrs.field(
        default=False,
        validator=attrs.validators.instance_of(bool),
        metadata={"location": ("request_filters", "trash_not_requested")},
    )
    """
    Whether or not to mark items in the inventory but not currently requested 
    for removal.
    """

    # @property
    # def trash_not_requested(self) -> Optional[bool]:
    #     """
    #     TODO
    #     """
    #     return self.request_filters.trash_not_requested

    # @trash_not_requested.setter
    # def trash_not_requested(self, value: Optional[bool]) -> None:
    #     if self.validate_assignment:
    #         result = attempt_and_reissue(
    #             self,
    #             type(self).Format.RequestFilters,
    #             self.request_filters,
    #             "trash_not_requested",
    #             value,
    #         )
    #         self.request_filters.trash_not_requested = result
    #     else:
    #         self.request_filters.trash_not_requested = value

    # =========================================================================

    request_from_buffers: bool = attrs.field(
        default=True,
        validator=attrs.validators.instance_of(bool),
        metadata={"location": ("request_filters", "request_from_buffers")},
    )
    """
    Whether or not this chest should request items from buffer chests in its 
    logistic network.
    """

    # @property
    # def request_from_buffers(self) -> Optional[bool]:
    #     """
    #     TODO
    #     """
    #     return self.request_filters["request_from_buffers"]

    # @request_from_buffers.setter
    # def request_from_buffers(self, value: Optional[bool]) -> None:
    #     if self.validate_assignment:
    #         result = attempt_and_reissue(
    #             self,
    #             type(self).Format.RequestFilters,
    #             self.request_filters,
    #             "request_from_buffers",
    #             value,
    #         )
    #         self.request_filters.request_from_buffers = result
    #     else:
    #         self.request_filters["request_from_buffers"] = value

    # =========================================================================

    requests_enabled: bool = attrs.field(
        default=True,
        validator=attrs.validators.instance_of(bool),
        metadata={"location": ("request_filters", "enabled")},
    )
    """
    Master toggle for all logistics requests on this entity. Superceeds any 
    logistic request toggles on any contained logistic sections.
    """

    # @property
    # def requests_enabled(self) -> Optional[bool]:
    #     """
    #     TODO
    #     """
    #     return self.request_filters.enabled

    # @requests_enabled.setter
    # def requests_enabled(self, value: Optional[bool]) -> None:
    #     if self.validate_assignment:
    #         result = attempt_and_reissue(
    #             self,
    #             type(self).Format.RequestFilters,
    #             self.request_filters,
    #             "enabled",
    #             value,
    #         )
    #         self.request_filters.enabled = result
    #     else:
    #         self.request_filters.enabled = value

    # =========================================================================

    sections: list[AttrsSection] = attrs.field(
        factory=list,
        # TODO: validators
        metadata={"location": ("request_filters", "sections")},
    )
    """
    The list of logistics sections that this entity is configured to request.
    """

    # @property
    # def sections(self) -> Optional[list[Section]]:
    #     """
    #     TODO
    #     """
    #     return self.request_filters.sections

    # @sections.setter
    # def sections(self, value: Optional[list[Section]]) -> None:
    #     if self.validate_assignment:
    #         result = attempt_and_reissue(
    #             self,
    #             type(self).Format.RequestFilters,
    #             self.request_filters,
    #             "sections",
    #             value,
    #         )
    #         self.request_filters.sections = result
    #     else:
    #         self.request_filters.sections = value

    # =========================================================================

    def add_section(
        self,
        group: Union[str, None] = None,
        index: Optional[int] = None,  # TODO: integer size
        active: bool = True,
    ) -> AttrsSection:
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
        # TODO: update
        section = {"active": active}
        if group is not None:
            section["group"] = group
        if index is not None:
            section["index"] = index + 1
        else:
            section["index"] = len(self.sections) + 1
        section = AttrsSection(**section)
        self.sections.append(section)
        return self.sections[-1]

    # =========================================================================

    def merge(self, other: "Entity"):
        super().merge(other)

        self.request_filters = other.request_filters

    # =========================================================================

    # def to_dict(
    #     self, exclude_none: bool = True, exclude_defaults: bool = True
    # ) -> dict:  # TODO: FIXME
    #     result = super().to_dict(
    #         exclude_none=exclude_none, exclude_defaults=exclude_defaults
    #     )
    #     if "request_filters" in result and result["request_filters"] == {}:
    #         del result["request_filters"]
    #     return result

    # =========================================================================

    # def __eq__(self, other) -> bool:
    #     return super().__eq__(other) and self.request_filters == other.request_filters
