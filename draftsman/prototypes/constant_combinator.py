# constant_combinator.py

from draftsman import __factorio_version_info__
from draftsman.classes.entity import Entity
from draftsman.classes.mixins import (
    PlayerDescriptionMixin,
    ControlBehaviorMixin,
    CircuitConnectableMixin,
    DirectionalMixin,
)
from draftsman.classes.vector import Vector, PrimitiveVector
from draftsman.constants import Direction, ValidationMode
from draftsman.data.signals import get_signal_types
from draftsman.error import DataFormatError
from draftsman.serialization import draftsman_converters
from draftsman.signatures import (
    ManualSection,
    uint32,
)
from draftsman.utils import fix_incorrect_pre_init
from draftsman.validators import instance_of
from draftsman.warning import PureVirtualDisallowedWarning  # TODO

from draftsman.data.entities import constant_combinators
from draftsman.data import entities

import attrs
from pydantic import ConfigDict, Field, ValidationError, field_validator
from typing import Any, Literal, Optional, Union


@fix_incorrect_pre_init
@attrs.define
class ConstantCombinator(
    PlayerDescriptionMixin,
    ControlBehaviorMixin,
    CircuitConnectableMixin,
    DirectionalMixin,
    Entity,
):
    """
    A combinator that holds a number of constant signals that can be output to
    the circuit network.
    """

    # class Format(
    #     PlayerDescriptionMixin.Format,
    #     ControlBehaviorMixin.Format,
    #     CircuitConnectableMixin.Format,
    #     DirectionalMixin.Format,
    #     Entity.Format,
    # ):
    #     # 1.1 Control behavior:
    #     # class ControlBehavior(DraftsmanBaseModel):
    #     #     filters: Optional[list[SignalFilter]] = Field(
    #     #         [],
    #     #         description="""
    #     #         The set of constant signals that are emitted when this
    #     #         combinator is turned on.
    #     #         """,
    #     #     )
    #     #     is_on: Optional[bool] = Field(
    #     #         True,
    #     #         description="""
    #     #         Whether or not this constant combinator is toggled on or off.
    #     #         """,
    #     #     )

    #     #     @field_validator("filters", mode="before")
    #     #     @classmethod
    #     #     def normalize_input(cls, value: Any):
    #     #         if isinstance(value, list):
    #     #             for i, entry in enumerate(value):
    #     #                 if isinstance(entry, tuple):
    #     #                     value[i] = {
    #     #                         "index": i + 1,
    #     #                         "signal": entry[0],
    #     #                         "count": entry[1],
    #     #                     }

    #     #         return value

    #     class ControlBehavior(DraftsmanBaseModel):
    #         sections: Optional[Sections] = Field(
    #             Sections(),
    #             description="""
    #             The signal sections specified in this combinator (or elsewhere?)
    #             """,
    #         )

    #         is_on: Optional[bool] = Field(
    #             True,
    #             description="""
    #             Whether or not this constant combinator is toggled on or off.
    #             """,
    #         )

    #     control_behavior: Optional[ControlBehavior] = ControlBehavior()

    #     model_config = ConfigDict(title="ConstantCombinator")

    # def __init__(
    #     self,
    #     name: Optional[str] = get_first(constant_combinators),
    #     position: Union[Vector, PrimitiveVector, None] = None,
    #     tile_position: Union[Vector, PrimitiveVector, None] = (0, 0),
    #     direction: Optional[Direction] = Direction.NORTH,
    #     player_description: Optional[str] = None,
    #     connections: Optional[Connections] = None,
    #     control_behavior: Optional[Format.ControlBehavior] = None,
    #     tags: Optional[dict[str, Any]] = None,
    #     validate_assignment: Union[
    #         ValidationMode, Literal["none", "minimum", "strict", "pedantic"]
    #     ] = ValidationMode.STRICT,
    #     **kwargs
    # ):
    #     """
    #     TODO
    #     """

    #     self._root: __class__.Format
    #     self.control_behavior: __class__.Format.ControlBehavior

    #     super().__init__(
    #         name,
    #         constant_combinators,
    #         position=position,
    #         tile_position=tile_position,
    #         direction=direction,
    #         player_description=player_description,
    #         connections={} if connections is None else connections,
    #         control_behavior={} if control_behavior is None else control_behavior,
    #         tags={} if tags is None else tags,
    #         **kwargs
    #     )

    #     self.validate_assignment = validate_assignment

    # =========================================================================

    @property
    def similar_entities(self) -> list[str]:
        return constant_combinators

    # =========================================================================

    @property
    def max_signal_count(self) -> uint32:
        """
        The total number of signals that this ``ConstantCombinator`` can
        hold. Equivalent to ``"item_slot_count"`` from Factorio's ``data.raw``.
        Returns ``None`` if the entity's name is not recognized by Draftsman.
        Not exported; read only.

        .. NOTE::

            In Factorio 1.0, this value returns the value of the
            ``"item_slot_count"`` key in ``data.raw``, which is usually 20
            signals. In Factorio 2.0, this value is 100 signal sections * 1000
            signals per section, for a total of 100,000 signals possible. Which
            value is returned is based on Draftsman's current environment
            version, which can be queried with TODO.
        """
        # TODO: better version query method
        if __factorio_version_info__ < (2, 0):  # pragma: no coverage
            return entities.raw.get(self.name, {"item_slot_count": None}).get(
                "item_slot_count", 20
            )
        else:
            return 100_000

    # =========================================================================

    # @property
    # def signals(self) -> Optional[list[SignalFilter]]:
    #     """
    #     The list of signals that this :py:class:`.ConstantCombinator` currently
    #     holds. Aliases ``control_behavior["filter"]``. Can be set to one of two
    #     formats:

    #     .. code-block:: python

    #         [{"index": int, "signal": SIGNAL_ID, "count": int}, ...]
    #         # Or
    #         [(signal_name, signal_value), (str, int), ...]

    #     If the data is set to the latter, it is converted to the former.

    #     Raises :py:class:`.DraftsmanWarning` if a signal is set to one of the
    #     pure virtual signals ("signal-everything", "signal-anything", or
    #     "signal-each").

    #     :getter: Gets the signals of the combinators, or an empty list if not
    #         set.
    #     :setter: Sets the signals of the combinators. Removes the key if set to
    #         ``None``.

    #     :exception DataFormatError: If set to anything that does not match the
    #         format specified above.
    #     """
    #     return self.control_behavior.sections.filters

    # @signals.setter
    # def signals(self, value: Optional[list[SignalFilter]]):
    #     if self.validate_assignment:
    #         result = attempt_and_reissue(
    #             self,
    #             type(self).Format.ControlBehavior,
    #             self.control_behavior,
    #             "filters",
    #             value,
    #         )
    #         self.control_behavior.sections.filters = result
    #     else:
    #         self.control_behavior.sections.filters = value

    def _sections_converter(value):
        if isinstance(value, list):
            for i, elem in enumerate(value):
                value[i] = ManualSection.converter(elem)
        return value

    sections: list[ManualSection] = attrs.field(
        factory=list,
        converter=_sections_converter,
        validator=instance_of(list[ManualSection]),
    )
    """
    TODO
    """

    # @property
    # def sections(self) -> Optional[list[Section]]:
    #     return self.control_behavior.sections.sections

    # @sections.setter
    # def sections(self, value: Optional[list[Section]]):
    #     if self.validate_assignment:
    #         result = attempt_and_reissue(
    #             self,
    #             type(self).Format.ControlBehavior.Sections,
    #             self.control_behavior.sections,
    #             "sections",
    #             value,
    #         )
    #         self.control_behavior.sections.sections = result
    #     else:
    #         self.control_behavior.sections.sections = value

    # =========================================================================

    enabled: bool = attrs.field(default=True, validator=instance_of(bool))
    """
    Whether or not this Constant combinator is "on" and currently outputting
    it's contents to connected wires. Default state is enabled.
    """

    # @property
    # def is_on(self) -> Optional[bool]:
    #     """
    #     Whether or not this Constant combinator is "on" and currently outputting
    #     it's contents to connected wires. Default state is enabled.

    #     :getter: Gets whether or not this combinator is enabled, or ``None`` if
    #         not set.
    #     :setter: Sets whether or not this combinator is enabled. Removes the key
    #         if set to ``None``.
    #     """
    #     return self.control_behavior.is_on

    # @is_on.setter
    # def is_on(self, value: Optional[bool]):
    #     if self.validate_assignment:
    #         result = attempt_and_reissue(
    #             self,
    #             type(self).Format.ControlBehavior,
    #             self.control_behavior,
    #             "is_on",
    #             value,
    #         )
    #         self.control_behavior.is_on = result
    #     else:
    #         self.control_behavior.is_on = value

    # =========================================================================

    def add_section(
        self,
        group: Union[str, None] = None,
        index: Optional[int] = None,  # TODO: integer size
        active: bool = True,
    ) -> ManualSection:
        """
        Adds a new section to the constant combinator.

        NOTE:: Beware of giving sections the same or existing names! If a named
            group already exists within a save, then that group will take
            precedence over a newly added group.

        NOTE:: When exporting combinators to a Factorio 1.0 string, only the
            first :py:attr:`.item_slot_count` filters of the first
            :py:class:`.Section` will be exported.

        :param group: The name to give this group. The group will have no name
            if omitted.
        :param index: The index at which to insert the filter group. Defaults to
            the end if omitted.
        :param active: Whether or not this particular group is contributing its
            contents to the output in this specific combinator.

        :returns: A reference to the :class:`.Section` just added.
        """
        self.sections += [
            ManualSection(
                group=group,
                index=index + 1 if index is not None else len(self.sections) + 1,
                active=active
            )
        ]
        return self.sections[-1]

    # =========================================================================

    # def set_signal(
    #     self,
    #     index: int64,
    #     name: str,
    #     count: int32 = 0,
    #     type: Optional[str] = None,
    #     quality: Literal["normal", "uncommon", "rare", "epic", "legendary"] = "normal"
    # ):
    #     """
    #     Set the signal of the ``ConstantCombinator`` at a particular index with
    #     a particular value.

    #     :param index: The index of the signal.
    #     :param signal: The name of the signal.
    #     :param count: The value of the signal.

    #     :exception TypeError: If ``index`` is not an ``int``, if ``name`` is not
    #         a ``str``, or if ``count`` is not an ``int``.
    #     """

    #     try:
    #         new_entry = SignalFilter(index=index, name=name, type=type, quality=quality, comparator="=", count=count)
    #         new_entry.index += 1
    #     except ValidationError as e:
    #         raise DataFormatError(e) from None

    #     section = self.sections[section]
    #     section.append(new_entry)

    #     new_filters = [] if self.signals is None else self.signals

    #     # # Check to see if filters already contains an entry with the same index
    #     # existing_index = None
    #     # for i, signal_filter in enumerate(new_filters):
    #     #     if index + 1 == signal_filter["index"]:  # Index already exists in the list
    #     #         if signal is None:  # Delete the entry
    #     #             del new_filters[i]
    #     #         else:
    #     #             new_filters[i] = new_entry
    #     #         existing_index = i
    #     #         break

    #     # if existing_index is None:
    #     #     new_filters.append(new_entry)

    # def get_signal(self, index: int64) -> Optional[SignalFilter]:
    #     """
    #     Get the :py:data:`.SIGNAL_FILTER` ``dict`` entry at a particular index,
    #     if it exists.

    #     :param index: The index of the signal to analyze.

    #     :returns: A ``dict`` that conforms to :py:data:`.SIGNAL_FILTER`, or
    #         ``None`` if nothing was found at that index.
    #     """
    #     filters = self.control_behavior.get("filters", None)
    #     if not filters:
    #         return None

    #     return next((item for item in filters if item["index"] == index + 1), None)

    # =========================================================================

    __hash__ = Entity.__hash__


draftsman_converters.add_hook_fns(
    # {"$id": "factorio:constant_combinator"},
    ConstantCombinator,
    lambda fields: {
        ("control_behavior", "is_on"): fields.enabled.name,
        ("control_behavior", "sections", "sections"): fields.sections.name,
    },
)
