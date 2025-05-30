# linked_belt.py

from draftsman.classes.entity import Entity
from draftsman.classes.mixins import DirectionalMixin
from draftsman.utils import fix_incorrect_pre_init

from draftsman.data.entities import linked_belts

import attrs


@fix_incorrect_pre_init
@attrs.define
class LinkedBelt(DirectionalMixin, Entity):  # TODO: finish
    """
    A belt object that can transfer items over any distance, regardless of
    constraint, as long as the two are paired together.

    .. WARNING::

        Functionally, currently unimplemented. Need to analyze how mods use this
        entity, as I can't seem to figure out the example one in the game.
    """

    @property
    def similar_entities(self) -> list[str]:
        return linked_belts

    # =========================================================================

    __hash__ = Entity.__hash__

