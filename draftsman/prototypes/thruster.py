# thruster.py

from draftsman.classes.entity import Entity

from draftsman.data.entities import thrusters

import attrs


@attrs.define
class Thruster(Entity):
    """
    An entity which accellerates space platforms.
    """

    @property
    def similar_entities(self) -> list[str]:
        return thrusters

    # =========================================================================

    __hash__ = Entity.__hash__
