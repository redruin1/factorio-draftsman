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


Thruster.add_schema(None, version=(1, 0))

Thruster.add_schema({"$id": "urn:factorio:entity:thruster"}, version=(2, 0))
