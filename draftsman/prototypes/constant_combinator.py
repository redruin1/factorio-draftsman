# constant_combinator.py

from draftsman.classes.entity import Entity
from draftsman.classes.mixins import (
    PlayerDescriptionMixin,
    ControlBehaviorMixin,
    CircuitConnectableMixin,
    DirectionalMixin,
)
from draftsman.serialization import draftsman_converters
from draftsman.signatures import (
    ManualSection,
    uint32,
)
from draftsman.utils import fix_incorrect_pre_init
from draftsman.validators import instance_of
from draftsman.data import mods

from draftsman.data.entities import constant_combinators
from draftsman.data import entities

import attrs
from typing import Optional, Union


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

    @property
    def similar_entities(self) -> list[str]:
        return constant_combinators

    # =========================================================================

    @property
    def max_signal_count(self) -> uint32:
        """
        The total number of signals that this ``ConstantCombinator`` can
        hold. Returns ``None`` if the entity's name is not recognized by
        Draftsman. Not exported; read only.

        .. NOTE::

            In Factorio 1.0, this value returns the value of the
            ``"item_slot_count"`` key in ``data.raw``, which is usually 20
            signals. In Factorio 2.0, this value is 100 signal sections * 1000
            signals per section, for a total of 100,000 possible unique signal
            definitions. Which value is returned is based on Draftsman's current
            environment version, which can be queried with
            :py:data:`draftsman.mods.versions`.
        """
        if mods.versions["base"] < (2, 0):  # pragma: no coverage
            return entities.raw.get(self.name, {"item_slot_count": None}).get(
                "item_slot_count", 20
            )
        else:
            return 100_000

    # =========================================================================

    def _sections_converter(value):
        if isinstance(value, list):
            for i, elem in enumerate(value):
                value[i] = ManualSection.converter(elem)
        return value

    sections: list[ManualSection] = attrs.field(
        factory=list,
        converter=_sections_converter,
        validator=instance_of(list[ManualSection]),  # TODO: max 100
    )
    """
    List of "manually" (player) defined signal section.

    .. NOTE::

        Beware of giving sections the same or existing names! If a named
        group already exists within a save, then the group that was defined
        first will overwrite all other data you try to specify.

    .. NOTE::

        When importing a constant combinator from a Factorio 1.0 string, the 
        :py:attr:`.item_slot_count` signals it contains will be added to the 
        first slots of the first :py:class:`.ManualSection` in this list.

        Similarly, when exporting a constant combinator to a Factorio 1.0 
        string, only the first :py:attr:`.item_slot_count` filters of the 
        first :py:class:`.ManualSection` will be exported.
    """

    # =========================================================================

    enabled: bool = attrs.field(default=True, validator=instance_of(bool))
    """
    Whether or not this Constant combinator is "on" and currently outputting
    it's contents to connected wires. Default state is enabled.
    """

    # =========================================================================

    def add_section(
        self,
        group: Union[str, None] = None,
        index: Optional[int] = None,  # TODO: integer size
        active: bool = True,
    ) -> ManualSection:
        """
        Adds a new section to the constant combinator.

        .. NOTE::

            Beware of giving sections the same or existing names! If a named
            group already exists within a save, then the group that was defined
            first will overwrite all other data you try to specify.

        :param group: The name to give this group. The group will have no name
            if omitted.
        :param index: The index at which to insert the filter group. Defaults to
            the end if omitted.
        :param active: Whether or not this particular group is contributing its
            contents to the output in this specific combinator.

        :returns: A reference to the :py:class:`.ManualSection` just added.
        """
        self.sections += [
            ManualSection(
                group=group,
                index=index + 1 if index is not None else len(self.sections) + 1,
                active=active,
            )
        ]
        return self.sections[-1]

    # =========================================================================

    __hash__ = Entity.__hash__


# TODO: 1.0 hook functions

draftsman_converters.add_hook_fns(
    ConstantCombinator,
    lambda fields: {
        ("control_behavior", "is_on"): fields.enabled.name,
        ("control_behavior", "sections", "sections"): fields.sections.name,
    },
)
