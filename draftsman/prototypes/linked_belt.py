# linked_belt.py

from draftsman.classes.entity import Entity
from draftsman.classes.mixins import DirectionalMixin

from draftsman.data.entities import linked_belts

import attrs


@attrs.define
class LinkedBelt(DirectionalMixin, Entity):
    """
    A belt object that can transfer items over any distance, regardless of
    constraint, as long as the two are paired together.

    .. NOTE::

        This class (currently) provides no functionality on actually linking
        belts together.
    """

    @property
    def similar_entities(self) -> list[str]:
        return linked_belts

    # =========================================================================

    __hash__ = Entity.__hash__
