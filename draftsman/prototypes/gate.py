# gate.py

from draftsman.classes.entity import Entity
from draftsman.classes.mixins import DirectionalMixin
from draftsman.utils import fix_incorrect_pre_init

from draftsman.data.entities import gates

import attrs


@fix_incorrect_pre_init
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


Gate.add_schema({"$id": "urn:factorio:entity:gate"})
