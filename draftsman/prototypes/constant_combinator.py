# constant_combinator.py

from draftsman import DEFAULT_FACTORIO_VERSION
from draftsman.classes.entity import Entity
from draftsman.classes.mixins import (
    PlayerDescriptionMixin,
    ControlBehaviorMixin,
    CircuitConnectableMixin,
    DirectionalMixin,
)
from draftsman.serialization import draftsman_converters
from draftsman.signatures import ManualSection, QualityID, SignalFilter, uint32
from draftsman.validators import instance_of
from draftsman.data import mods

from draftsman.data.entities import constant_combinators
from draftsman.data import entities

import attrs
from typing import Optional


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

    @property
    def similar_entities(self) -> list[str]:
        return constant_combinators

    # =========================================================================

    @property
    def max_signal_count(self) -> uint32:
        """
        The total number of signals that this entity can hold. Returns ``None``
        if the entity's name is not recognized by Draftsman.

        .. NOTE::

            In Factorio 1.0, this value returns the value of the
            ``"item_slot_count"`` key in ``data.raw``, which is usually 20
            signals. In Factorio 2.0, this value is 100 signal sections * 1000
            signals per section, for a total of 100,000 possible unique signal
            definitions. Which value is returned is based on Draftsman's current
            environment version, which can be queried with
            :py:data:`draftsman.mods.versions`.
        """
        if mods.versions.get("base", DEFAULT_FACTORIO_VERSION) < (2, 0):
            return entities.raw.get(self.name, {"item_slot_count": None}).get(
                "item_slot_count"
            )
        else:
            return 100_000

    # =========================================================================

    sections: list[ManualSection] = attrs.field(
        factory=list,
        validator=instance_of(list[ManualSection]),
    )
    """
    .. serialized::

        This attribute is imported/exported from blueprint strings.

    List of "manually" (player) defined signal sections.

    .. NOTE::

        When importing a constant combinator from a Factorio 1.0 string, the 
        first :py:attr:`.max_signal_count` (usually 20) signals it contains will 
        be added to the first slots of the first :py:class:`.ManualSection` in 
        this list.

        Similarly, when exporting a constant combinator to a Factorio 1.0 
        string, only the first :py:attr:`.max_signal_count` filters of the 
        first :py:class:`.ManualSection` will be exported.

    .. WARNING::

        Beware of giving sections the same or existing names! If a named
        group already exists within a save, then the group that already exists
        in the save will overwrite whatever new values you define.
    """

    # =========================================================================

    enabled: bool = attrs.field(default=True, validator=instance_of(bool))
    """
    .. serialized::

        This attribute is imported/exported from blueprint strings.

    Whether or not this Constant combinator is "on" and currently outputting
    it's contents to connected wires. Default state is enabled.
    """

    # =========================================================================

    def add_section(
        self,
        group: Optional[str] = None,
        index: Optional[int] = None,  # TODO: should be int64
        active: bool = True,
    ) -> ManualSection:
        """
        Adds a new section to the constant combinator.

        .. WARNING::

            Beware of giving sections the same or existing names! If a named
            group already exists within a save, then the group that already
            exists in the save will overwrite whatever new values you define.

        :param group: The name to give this group. The group will have no name
            if omitted.
        :param index: The index at which to insert the filter group. Defaults to
            the end if omitted.
        :param active: Whether or not this particular group is contributing its
            contents to the output in this specific combinator.

        :returns: A reference to the :py:class:`.ManualSection` just added.
        """
        print("add_section")
        self.sections += [
            ManualSection(
                group=group,
                index=index if index is not None else len(self.sections),
                active=active,
            )
        ]
        return self.sections[-1]

    # =========================================================================

    def set_signal(
        self,
        index: int,  # TODO: should be int64
        name: Optional[str],  # TODO: should be SignalIDName
        count: int = 0,  # TODO: should be int32
        quality: QualityID = "normal",
        type: Optional[str] = None,
    ) -> None:
        """
        Sets a particular signal in this constant combinator.

        This function does all of the signal section management for you, acting
        as if the constant combinator has one big, unnamed signal group rather
        than multiple individual groups. This is useful if you just want to
        treat the CC as a black box that outputs the given signals with the
        given values for simple cases.

        What signal section defined signals will reside in is determined by
        their ``index // 1000``; so a signal set at index 999 will be in the
        0th signal section, while a signal set at index 1000 will be in the
        1st signal section, and so on.

        In order to prevent collisions between identical signal types in the
        same group, this method prohibits setting the same signal in at two
        different indexes at the same time (following the concept of "one big
        signal section"). If this is troublesome, users should instead use
        :py:meth:`.add_section` and perform the grouping themselves manually.

        :param index: The index of the signal in the GUI.
        :param name: The name of the signal.
        :param count: The amount of the item/the value to output.
        :param quality: The quality of the signal.
        :param type: The internal type of the signal.
        """
        section_index = index // 1000
        # TODO: this might be slow
        section = next(
            # Try and an existing section with that particular index...
            (section for section in self.sections if section.index == section_index),
            None,
        )
        # ... or create a new one if it doesn't exist
        if section is None:
            section = self.add_section(index=section_index)

        section.set_signal(
            index=index % 1000, name=name, count=count, quality=quality, type=type
        )

    # =========================================================================

    def get_signal(self, index: int) -> Optional[SignalFilter]:
        """
        Gets a particular signal inside of this constant combinator.

        :returns: A :py:class:`.SignalFilter` instance, or ``None`` if nothing
            was found at that index.
        """
        section_index = index // 1000
        # TODO: this might be slow
        section = next(
            # Try and an existing section with that particular index
            (section for section in self.sections if section.index == section_index),
            None,
        )
        # If it doesn't exist, clearly there's no signal there
        if section is None:
            return None

        return section.get_signal(index=index % 1000)

    # =========================================================================

    __hash__ = Entity.__hash__


draftsman_converters.get_version((1, 0)).add_hook_fns(
    ConstantCombinator,
    lambda fields, converter: {
        ("control_behavior", "is_on"): fields.enabled.name,
        ("control_behavior", "filters"): (
            fields.sections,
            lambda value, _, inst, args: [
                ManualSection(
                    index=0,
                    filters=[converter.structure(elem, SignalFilter) for elem in value],
                )
            ],
        ),
    },
    lambda fields, converter: {
        ("control_behavior", "is_on"): fields.enabled.name,
        ("control_behavior", "filters"): (
            fields.sections,
            lambda inst: (
                [
                    converter.unstructure(signal)
                    for signal in inst.sections[0].filters.values()
                ]
                if len(inst.sections) > 0
                else []
            ),
        ),
    },
)

draftsman_converters.get_version((2, 0)).add_hook_fns(
    ConstantCombinator,
    lambda fields: {
        ("control_behavior", "is_on"): fields.enabled.name,
        ("control_behavior", "sections", "sections"): fields.sections.name,
    },
)
