# gate.py

from draftsman.classes.entity import Entity
from draftsman.classes.mixins import DirectionalMixin

from draftsman.data.entities import gates

import attrs


@attrs.define
class Gate(DirectionalMixin, Entity):
    """
    A wall that opens near the player.
    """

    @property
    def similar_entities(self) -> list[str]:
        return gates

    # =========================================================================

    __hash__ = Entity.__hash__
